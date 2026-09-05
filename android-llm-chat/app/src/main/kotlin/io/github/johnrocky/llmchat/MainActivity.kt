package io.github.johnrocky.llmchat

import android.app.Activity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.ScrollView
import android.widget.TextView
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * A plain Activity that hosts the recipe: Send streams a reply, Stop cancels the reply being
 * generated, Release model frees the engine (and Load model brings it back). The value is in
 * ChatEngine and ModelProvisioner; this file only shows how to drive them from a UI.
 */
class MainActivity : Activity() {

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private var chatEngine: ChatEngine? = null
    private var replyJob: Job? = null
    private var releasing = false

    private lateinit var status: TextView
    private lateinit var transcript: TextView
    private lateinit var transcriptScroll: ScrollView
    private lateinit var prompt: EditText
    private lateinit var send: Button
    private lateinit var stop: Button
    private lateinit var release: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        status = findViewById(R.id.status)
        transcript = findViewById(R.id.transcript)
        transcriptScroll = findViewById(R.id.transcript_scroll)
        prompt = findViewById(R.id.prompt)
        send = findViewById(R.id.send)
        stop = findViewById(R.id.stop)
        release = findViewById(R.id.release)

        send.isEnabled = false
        stop.isEnabled = false
        release.isEnabled = false
        send.setOnClickListener { onSend() }
        // Stop: cancelling the collecting coroutine stops the model too (see ChatEngine.send).
        // chatEngine?.cancel() does the same from code that does not hold the Job.
        stop.setOnClickListener { replyJob?.cancel() }
        release.setOnClickListener { if (chatEngine?.isInitialized == true) onRelease() else loadModel() }

        loadModel()
    }

    private fun loadModel() {
        release.isEnabled = false
        scope.launch {
            try {
                status.text = "Preparing model"
                val modelFile = ModelProvisioner.provision(
                    context = this@MainActivity,
                    url = BuildConfig.MODEL_URL,
                    sha256 = BuildConfig.MODEL_SHA256,
                    expectedBytes = BuildConfig.MODEL_BYTES,
                ) { message -> scope.launch { status.text = message } }
                status.text = "Loading model (slow on the first run)"
                val engine = chatEngine ?: ChatEngine(modelFile.absolutePath, cacheDir.path).also { chatEngine = it }
                engine.initialize()
                status.text = "Ready: ${modelFile.name} on LiteRT-LM ${BuildConfig.LITERTLM_VERSION}"
                send.isEnabled = true
                release.text = getString(R.string.release)
            } catch (e: Exception) {
                status.text = "Setup failed: ${e.message}"
            } finally {
                release.isEnabled = true
            }
        }
    }

    private fun onRelease() {
        val engine = chatEngine ?: return
        releasing = true
        replyJob?.cancel()
        send.isEnabled = false
        stop.isEnabled = false
        release.isEnabled = false
        scope.launch {
            // close() stops a reply in flight and waits for the native side to finish it, so it
            // runs off the main thread.
            withContext(Dispatchers.IO) { engine.close() }
            releasing = false
            status.text = "Model released"
            release.text = getString(R.string.load)
            release.isEnabled = true
        }
    }

    private fun onSend() {
        val engine = chatEngine?.takeIf { it.isInitialized } ?: return
        val text = prompt.text.toString().trim()
        if (text.isEmpty()) return
        prompt.text.clear()
        send.isEnabled = false
        stop.isEnabled = true
        append("You: $text\n")
        append("Model: ")
        replyJob = scope.launch {
            try {
                engine.send(text)
                    .catch { e -> append("[error: ${e.message}]") }
                    // Chunks are incremental: append, never replace.
                    .collect { chunk -> append(chunk) }
            } finally {
                append("\n\n")
                send.isEnabled = !releasing && engine.isInitialized
                stop.isEnabled = false
            }
        }
    }

    private fun append(text: String) {
        transcript.append(text)
        transcriptScroll.post { transcriptScroll.fullScroll(ScrollView.FOCUS_DOWN) }
    }

    override fun onDestroy() {
        super.onDestroy()
        scope.cancel()
        // Stops a reply in flight and frees the model; blocks for about one decode step at most.
        chatEngine?.close()
        chatEngine = null
    }
}
