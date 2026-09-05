package io.github.johnrocky.llmchat

import com.google.ai.edge.litertlm.Backend
import com.google.ai.edge.litertlm.BenchmarkInfo
import com.google.ai.edge.litertlm.Contents
import com.google.ai.edge.litertlm.Conversation
import com.google.ai.edge.litertlm.ConversationConfig
import com.google.ai.edge.litertlm.Engine
import com.google.ai.edge.litertlm.EngineConfig
import com.google.ai.edge.litertlm.ExperimentalApi
import com.google.ai.edge.litertlm.Message
import com.google.ai.edge.litertlm.SamplerConfig
import java.util.concurrent.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.emitAll
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onCompletion
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.withContext

/**
 * The one file that touches the LiteRT-LM API. Copy it into your project and change the
 * package line; nothing here depends on Android UI types.
 *
 * Lifecycle: [initialize] (slow, seconds) -> any number of [send] turns -> [close]. After
 * [close] you may call [initialize] again on the same instance and the chat continues where it
 * was: that is how an app frees the model's memory in the background and reloads it later.
 * Call [initialize] and [close] from one place at a time (an Activity or a ViewModel); [send]
 * flows may be collected on any dispatcher and [cancel] may be called from any thread.
 *
 * Every class used here lives in `com.google.ai.edge.litertlm`. If you remember
 * `org.tensorflow.*` or Interpreter-style APIs, that memory is from the TFLite era.
 */
class ChatEngine(
    private val modelPath: String,
    // Compilation cache: the second load is much faster. Pass context.cacheDir.path.
    private val cacheDir: String?,
    // CPU works on every device with no manifest changes. Backend.GPU() needs the two
    // <uses-native-library> entries in AndroidManifest.xml; when it fails to initialize, show
    // the error rather than falling back silently, or a slow path looks like a working one.
    private val backend: Backend = Backend.CPU(),
    private val systemInstruction: String = "You are a helpful assistant.",
) : AutoCloseable {

    @Volatile private var engine: Engine? = null
    @Volatile private var conversation: Conversation? = null

    // The chat as the model sees it: completed user and model turns in order. It outlives the
    // runtime's Conversation object, which is rebuilt from it after a cancel and after
    // close()+initialize(). A cancelled turn is not added: with the cut-off reply in the history
    // the model continued that reply instead of answering the next prompt (measured on a Pixel
    // 8a, twice, byte-identical), and the runtime's own cancel path drops the turn too. Show the
    // partial text in your UI if you want to; the model does not see it again.
    private val history = mutableListOf<Message>()

    // Set by a cancel. The runtime documents that a session is not reusable after
    // cancelProcess() (in practice the next reply comes back empty), so the next send() replaces
    // the Conversation with a new one seeded from `history`. That re-prefills the chat once.
    @Volatile private var conversationStale = false

    // True while a send() flow is running, from its first runtime call to its completion.
    @Volatile private var generating = false

    val isInitialized: Boolean
        get() = engine != null

    /** The completed turns so far, oldest first. Cancelled turns are not included. */
    val turns: List<Message>
        get() = synchronized(history) { history.toList() }

    /**
     * Loads the model and opens the conversation (seeded with earlier turns, if any). Confined
     * to Dispatchers.IO because a GB-scale load on the main thread is an ANR.
     */
    suspend fun initialize(): Unit = withContext(Dispatchers.IO) {
        check(engine == null) { "already initialized; call close() first" }
        val newEngine = Engine(EngineConfig(modelPath = modelPath, backend = backend, cacheDir = cacheDir))
        try {
            newEngine.initialize()
            conversation = newEngine.createConversation(conversationConfig())
            conversationStale = false
            engine = newEngine
        } catch (e: Exception) {
            conversation?.close()
            conversation = null
            newEngine.close()
            throw e
        }
    }

    /**
     * Streams the reply to [prompt] as incremental chunks; concatenate them on the collecting
     * side. Turns share one chat, so the model sees the earlier turns.
     *
     * Stopping: cancel the coroutine that collects this flow and generation stops on the native
     * side too (the runtime's own flow does not do that by itself: its `awaitClose` is empty, so
     * a cancelled collector would leave the model decoding to the end). Or call [cancel] from
     * anywhere; then this flow completes normally with the text produced so far. Either way the
     * next send() works; it rebuilds the runtime conversation first, which costs one prefill of
     * the chat so far, and the cancelled turn is left out of that chat (see `history`).
     *
     * Errors surface through the flow (`.catch`), which is how the runtime's callback reports them.
     */
    fun send(prompt: String): Flow<String> = flow {
        generating = true
        try {
            val conv = withContext(Dispatchers.IO) { currentConversation() }
            val reply = StringBuilder()
            emitAll(
                conv.sendMessageAsync(prompt)
                    .map { it.toString() }
                    .onEach { reply.append(it) }
                    .onCompletion { cause ->
                        // Reached with a CancellationException both when the collector is
                        // cancelled and when cancel() or close() stopped the runtime (it reports
                        // that as kCancelled). cancelProcess() is a no-op once generation ended.
                        if (cause is CancellationException) {
                            runCatching { conv.cancelProcess() }
                            conversationStale = true
                        } else if (cause == null) {
                            synchronized(history) {
                                history += Message.user(prompt)
                                history += Message.model(reply.toString())
                            }
                        }
                    }
                    .catch { e ->
                        // A cancel() reaches the collector as CancellationException; end quietly.
                        if (e !is CancellationException) throw e
                    }
            )
        } finally {
            generating = false
        }
    }

    /**
     * Stops the reply that is being generated, if any; a no-op when idle. The flow returned by
     * [send] completes with the chunks delivered so far, and the next [send] continues the chat.
     */
    fun cancel() {
        if (!generating) return
        conversationStale = true
        conversation?.let { runCatching { it.cancelProcess() } }
    }

    /**
     * Tokens per second and time to first token of the last turn, from the runtime itself. Only
     * available when `ExperimentalFlags.enableBenchmark = true` was set before [initialize];
     * otherwise the runtime throws. Optional: nothing else here depends on it.
     */
    @OptIn(ExperimentalApi::class)
    fun benchmarkInfo(): BenchmarkInfo =
        checkNotNull(conversation) { "call initialize() first" }.getBenchmarkInfo()

    /**
     * Releases the model and its memory; the chat history is kept for the next [initialize].
     * Safe to call while a reply is being generated: the reply is cancelled first, because
     * deleting the native conversation waits for the work in flight to finish, so without the
     * cancel this call would block until the end of the reply. Order matters: the conversation
     * borrows the engine's native resources, so it goes first. Idempotent.
     */
    override fun close() {
        conversation?.let { conv ->
            runCatching { conv.cancelProcess() }
            conversation = null
            conv.close()
        }
        engine?.close()
        engine = null
    }

    private fun currentConversation(): Conversation {
        val engine = checkNotNull(engine) { "call initialize() first" }
        val current = conversation
        if (current != null && !conversationStale) return current
        current?.close()
        return engine.createConversation(conversationConfig()).also {
            conversation = it
            conversationStale = false
        }
    }

    private fun conversationConfig() = ConversationConfig(
        systemInstruction = Contents.of(systemInstruction),
        initialMessages = turns,
        // SamplerConfig has no defaults; these are the values the LiteRT-LM samples use.
        samplerConfig = SamplerConfig(topK = 40, topP = 0.9, temperature = 0.7),
    )
}
