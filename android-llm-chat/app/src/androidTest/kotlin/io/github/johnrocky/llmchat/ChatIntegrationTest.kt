package io.github.johnrocky.llmchat

import android.os.Build
import android.os.Debug
import android.os.PowerManager
import android.os.SystemClock
import android.system.Os
import android.system.OsConstants
import android.util.Log
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.google.ai.edge.litertlm.Backend
import com.google.ai.edge.litertlm.ExperimentalApi
import com.google.ai.edge.litertlm.ExperimentalFlags
import java.io.File
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.FixMethodOrder
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.MethodSorters

/**
 * The verify command's test: what an integration must do, in five checks.
 *
 * 1. A fixed prompt streams a non-empty reply; a second turn in the same conversation works.
 * 2. Cancelling the coroutine that collects the reply stops generation on the native side:
 *    the process's CPU time stays flat for 1.5 s afterwards, no chunk arrives after the cancel,
 *    and the conversation accepts the next prompt.
 * 3. An explicit ChatEngine.cancel() ends the flow normally with the partial text.
 * 4. close() releases the model; initialize() on the same instance brings it back.
 * 5. close() while a reply is streaming returns promptly (the reply is cancelled first), the
 *    process goes idle, and initialize() + the next prompt work.
 *
 * Run (push the model first, or let the first test download it):
 *   adb push <model file> /sdcard/Android/data/io.github.johnrocky.llmchat/files/
 *   ./gradlew :app:connectedDebugAndroidTest -Pandroid.injected.androidTest.leaveApksInstalledAfterRun=true
 * Without the last flag Gradle uninstalls the app after the run, which also deletes the pushed
 * model and the runtime's cache. Add -Pandroid.testInstrumentationRunnerArguments.backend=gpu
 * for the GPU backend.
 * Each check logs one "RESULT" line under the logcat tag "recipe"; INTEGRATION.md quotes them.
 */
@RunWith(AndroidJUnit4::class)
@FixMethodOrder(MethodSorters.NAME_ASCENDING)
class ChatIntegrationTest {

    private val context = InstrumentationRegistry.getInstrumentation().targetContext
    private val backendName: String = InstrumentationRegistry.getArguments().getString("backend") ?: "cpu"
    private lateinit var modelFile: File

    @OptIn(ExperimentalApi::class)
    @Before
    fun provision(): Unit = runBlocking {
        // Lets ChatEngine.benchmarkInfo() report the runtime's own tokens/s. Not needed in an app.
        ExperimentalFlags.enableBenchmark = true
        val pushed = File(context.getExternalFilesDir(null), BuildConfig.MODEL_URL.substringAfterLast('/'))
        val cached = File(context.filesDir, "models/" + BuildConfig.MODEL_URL.substringAfterLast('/'))
        val via = when {
            pushed.length() == BuildConfig.MODEL_BYTES -> "pushed"
            cached.length() == BuildConfig.MODEL_BYTES -> "cached"
            else -> "download"
        }
        val t0 = SystemClock.elapsedRealtime()
        modelFile = ModelProvisioner.provision(
            context = context,
            url = BuildConfig.MODEL_URL,
            sha256 = BuildConfig.MODEL_SHA256,
            expectedBytes = BuildConfig.MODEL_BYTES,
            onProgress = {},
        )
        // Logged once per test; "download" means the sha256-verified download path ran here.
        Log.i("recipe", "PROVISION via=$via ms=${SystemClock.elapsedRealtime() - t0} bytes=${modelFile.length()} path=${modelFile.path}")
    }

    @Test
    fun a_fixedPromptStreamsAReplyAndASecondTurnWorks() = runBlocking {
        newEngine().use { engine ->
            val loadMs = timed { engine.initialize() }
            val first = collectAll(engine.send(PROMPT))
            assertTrue("expected a non-blank streamed reply", first.text.isNotBlank())
            assertTrue("expected streaming (>0 chunks)", first.chunks > 0)
            val b = engine.benchmarkInfo()
            val second = collectAll(engine.send("Now answer the same question in five words or fewer."))
            assertTrue("expected a non-blank second turn", second.text.isNotBlank())
            val b2 = engine.benchmarkInfo()
            result(
                "turn",
                "load_ms=$loadMs chunks=${first.chunks} chars=${first.text.length} " +
                    "first_chunk_ms=${first.firstChunkMs} total_ms=${first.totalMs} " +
                    "prefill_tokens=${b.lastPrefillTokenCount} decode_tokens=${b.lastDecodeTokenCount} " +
                    "prefill_tok_s=${fmt(b.lastPrefillTokensPerSecond)} decode_tok_s=${fmt(b.lastDecodeTokensPerSecond)} " +
                    "ttft_s=${fmt(b.timeToFirstTokenInSecond)} reply=${quote(first.text)} " +
                    "second_turn_chunks=${second.chunks} second_turn_chars=${second.text.length} " +
                    "second_prefill_tokens=${b2.lastPrefillTokenCount} second_decode_tokens=${b2.lastDecodeTokenCount} " +
                    "second_prefill_tok_s=${fmt(b2.lastPrefillTokensPerSecond)} second_decode_tok_s=${fmt(b2.lastDecodeTokensPerSecond)} " +
                    "second_ttft_s=${fmt(b2.timeToFirstTokenInSecond)} second_reply=${quote(second.text)}",
            )
            // Throughput on a reply long enough to measure: three turns, the runtime's own numbers.
            val thermalBefore = thermalStatus()
            val decode = mutableListOf<Double>()
            val prefill = mutableListOf<Double>()
            val ttft = mutableListOf<Double>()
            val decodeTokens = mutableListOf<Int>()
            repeat(3) {
                val r = collectAll(engine.send(BENCH_PROMPT))
                assertTrue(r.text.isNotBlank())
                val bi = engine.benchmarkInfo()
                decode += bi.lastDecodeTokensPerSecond
                prefill += bi.lastPrefillTokensPerSecond
                ttft += bi.timeToFirstTokenInSecond
                decodeTokens += bi.lastDecodeTokenCount
            }
            result(
                "throughput",
                "prompt=${quote(BENCH_PROMPT)} runs=3 decode_tokens=${decodeTokens.joinToString("/")} " +
                    "decode_tok_s=${decode.joinToString("/") { fmt(it) }} decode_tok_s_median=${fmt(decode.sorted()[1])} " +
                    "prefill_tok_s=${prefill.joinToString("/") { fmt(it) }} ttft_s=${ttft.joinToString("/") { fmt(it) }} " +
                    "thermal_status=$thermalBefore->${thermalStatus()}",
            )
        }
    }

    @Test
    fun b_cancellingTheCollectorStopsGeneration() = runBlocking {
        newEngine().use { engine ->
            engine.initialize()
            // Turn 1 establishes a fact the last turn must still know after the cancel.
            // No fixed reply word here: told to answer "Noted", the GPU build later parroted "Noted"
            // to the name question instead of recalling the name.
            val intro = collectAll(engine.send("Hello! My name is Alice."))
            assertTrue(intro.text.isNotBlank())
            var chunks = 0
            var completedOnItsOwn = false
            val job = launch(Dispatchers.Default) {
                engine.send(LONG_PROMPT).collect { chunks++ }
                completedOnItsOwn = true
            }
            withTimeout(120_000) { while (chunks < 5) delay(20) }
            // Control: how much CPU time generation burns per 500 ms while it is running.
            val generating = cpuOverMs(500)
            assertFalse("the reply ended before the cancel; this run tested nothing", completedOnItsOwn)
            job.cancelAndJoin()
            val chunksAtCancel = chunks
            delay(300)
            // The claim: after the cancel, the process is idle.
            val idle = cpuOverMs(1500)
            assertEquals("chunks arrived after the cancel", chunksAtCancel, chunks)
            assertTrue(
                "process CPU time after cancel: ${idle.cpuMs} ms over ${idle.wallMs} ms wall (while generating: ${generating.cpuMs} ms over ${generating.wallMs} ms)",
                idle.cpuMs < 400,
            )
            // The chat continues: the rebuilt conversation carries turn 1, not the cancelled turn.
            val next = collectAll(engine.send("What is my name? Answer with the name only."))
            assertTrue("expected the earlier turn to survive the cancel, got: ${next.text}", next.text.contains("Alice", ignoreCase = true))
            result(
                "cancel_collector",
                "chunks_before_cancel=$chunksAtCancel cpu_ms_generating=${generating.cpuMs}/${generating.wallMs}ms " +
                    "cpu_ms_after_cancel=${idle.cpuMs}/${idle.wallMs}ms next_turn_chars=${next.text.length} " +
                    "next_turn_first_chunk_ms=${next.firstChunkMs} turns=${engine.turns.size} " +
                    "intro_reply=${quote(intro.text)} next_turn_reply=${quote(next.text)}",
            )
        }
    }

    @Test
    fun c_explicitCancelEndsTheFlowWithThePartialText() = runBlocking {
        newEngine().use { engine ->
            engine.initialize()
            val text = StringBuilder()
            var chunks = 0
            val collector = async(Dispatchers.Default) {
                val t0 = SystemClock.elapsedRealtime()
                engine.send(LONG_PROMPT).collect { chunk ->
                    text.append(chunk)
                    if (++chunks == 5) engine.cancel()
                }
                SystemClock.elapsedRealtime() - t0
            }
            val completedMs = withTimeout(120_000) { collector.await() }
            val chunksAtCompletion = chunks
            assertTrue("expected the flow to end right after the cancel at chunk 5, got $chunksAtCompletion chunks", chunksAtCompletion in 5..8)
            delay(300)
            val idle = cpuOverMs(1500)
            assertTrue("expected the partial text", text.isNotBlank())
            assertEquals("chunks arrived after the flow completed", chunksAtCompletion, chunks)
            assertTrue("process CPU time after cancel: ${idle.cpuMs} ms over ${idle.wallMs} ms", idle.cpuMs < 400)
            val next = collectAll(engine.send("Say OK."))
            assertTrue("expected a fresh answer to the next prompt, got: ${next.text}", next.text.contains("ok", ignoreCase = true) && next.text.length < 200)
            result(
                "cancel_explicit",
                "chunks=$chunksAtCompletion chars=${text.length} flow_completed_ms=$completedMs " +
                    "cpu_ms_after_cancel=${idle.cpuMs}/${idle.wallMs}ms next_turn_chars=${next.text.length} " +
                    "next_turn_first_chunk_ms=${next.firstChunkMs} turns=${engine.turns.size} " +
                    "partial=${quote(text.toString())} next_turn_head=${quote(next.text)}",
            )
        }
    }

    @Test
    fun d_closeReleasesTheModelAndInitializeAgainWorks() = runBlocking {
        val engine = newEngine()
        val load1 = timed { engine.initialize() }
        val first = collectAll(engine.send(PROMPT))
        assertTrue(first.text.isNotBlank())
        val pssLoadedKb = Debug.getPss()
        engine.close()
        assertFalse(engine.isInitialized)
        delay(500)
        val pssReleasedKb = Debug.getPss()
        val load2 = timed { engine.initialize() }
        val second = collectAll(engine.send(PROMPT))
        assertTrue("expected a reply after close() + initialize()", second.text.isNotBlank())
        engine.close()
        result(
            "release",
            "load1_ms=$load1 pss_loaded_kb=$pssLoadedKb pss_released_kb=$pssReleasedKb load2_ms=$load2 " +
                "reply_chars_after_reload=${second.text.length} turns_after_reload=${engine.turns.size}",
        )
    }

    @Test
    fun e_closeDuringGenerationStopsItAndInitializeAgainWorks() = runBlocking {
        val engine = newEngine()
        engine.initialize()
        var chunks = 0
        val job = launch(Dispatchers.Default) {
            engine.send(LONG_PROMPT).collect { chunks++ }
        }
        withTimeout(120_000) { while (chunks < 5) delay(20) }
        // Release model while streaming, as an app would from a button or from onDestroy.
        val closeMs = timed { withContext(Dispatchers.IO) { engine.close() } }
        withTimeout(30_000) { job.join() }
        val chunksAtClose = chunks
        assertFalse(engine.isInitialized)
        delay(300)
        val idle = cpuOverMs(1500)
        assertTrue("close() during generation took $closeMs ms", closeMs < 10_000)
        assertTrue("process CPU time after close: ${idle.cpuMs} ms over ${idle.wallMs} ms", idle.cpuMs < 400)
        val reloadMs = timed { engine.initialize() }
        val next = collectAll(engine.send("Say OK."))
        assertTrue("expected a reply after close() during generation + initialize()", next.text.isNotBlank())
        engine.close()
        result(
            "close_during_generation",
            "chunks_at_close=$chunksAtClose close_ms=$closeMs cpu_ms_after_close=${idle.cpuMs}/${idle.wallMs}ms " +
                "reload_ms=$reloadMs next_turn_chars=${next.text.length} next_turn_first_chunk_ms=${next.firstChunkMs} " +
                "turns=${engine.turns.size} next_turn_head=${quote(next.text)}",
        )
    }

    // ---- helpers ----

    private fun backend(): Backend = if (backendName == "gpu") Backend.GPU() else Backend.CPU()

    private fun newEngine() = ChatEngine(modelFile.absolutePath, context.cacheDir.path, backend())

    private class Collected(val text: String, val chunks: Int, val firstChunkMs: Long, val totalMs: Long)

    private suspend fun collectAll(flow: Flow<String>): Collected {
        val text = StringBuilder()
        var chunks = 0
        var firstChunkMs = -1L
        val t0 = SystemClock.elapsedRealtime()
        withTimeout(300_000) {
            flow.collect { chunk ->
                if (chunks == 0) firstChunkMs = SystemClock.elapsedRealtime() - t0
                text.append(chunk)
                chunks++
            }
        }
        return Collected(text.toString(), chunks, firstChunkMs, SystemClock.elapsedRealtime() - t0)
    }

    private suspend fun timed(block: suspend () -> Unit): Long {
        val t0 = SystemClock.elapsedRealtime()
        block()
        return SystemClock.elapsedRealtime() - t0
    }

    private class CpuSample(val cpuMs: Long, val wallMs: Long)

    /** CPU time (user + system, all threads of this process) consumed during a wait of [ms]. */
    private suspend fun cpuOverMs(ms: Long): CpuSample {
        val cpu0 = processCpuMs()
        val t0 = SystemClock.elapsedRealtime()
        delay(ms)
        return CpuSample(processCpuMs() - cpu0, SystemClock.elapsedRealtime() - t0)
    }

    private fun processCpuMs(): Long {
        val stat = File("/proc/self/stat").readText()
        val fields = stat.substring(stat.lastIndexOf(')') + 2).split(' ')
        val ticks = fields[11].toLong() + fields[12].toLong() // utime + stime, fields 14 and 15
        return ticks * 1000 / Os.sysconf(OsConstants._SC_CLK_TCK)
    }

    private fun fmt(d: Double) = String.format(java.util.Locale.US, "%.2f", d)

    /** PowerManager thermal status (0 = none .. 6 = shutdown), -1 below API 29. */
    private fun thermalStatus(): Int =
        if (Build.VERSION.SDK_INT >= 29) context.getSystemService(PowerManager::class.java).currentThermalStatus else -1

    /** First 80 characters of a reply on one line, for the RESULT log. */
    private fun quote(text: String) = "\"" + text.take(80).replace("\n", " ").replace("\"", "'") + "\""

    private fun result(check: String, values: String) {
        Log.i(
            "recipe",
            "RESULT check=$check device=${Build.MODEL} sdk=${Build.VERSION.SDK_INT} " +
                "backend=$backendName litertlm=${BuildConfig.LITERTLM_VERSION} model=${modelFile.name} $values",
        )
    }

    private companion object {
        const val PROMPT = "In one sentence, what is the capital of France?"
        const val LONG_PROMPT = "Count from 1 to 400, separated by commas, with no other text."
        const val BENCH_PROMPT = "Explain in five sentences why the sky is blue."
    }
}
