# Add a chat that needs no network to an existing Android app (Qwen2.5-1.5B-Instruct on LiteRT-LM)

**Short answer.** Add two Gradle lines, copy two Kotlin files, and let the app download one
1.6 GB model file once. You get streaming replies from Qwen2.5-1.5B-Instruct computed entirely on
the phone, a Stop that really stops the model, and a Release that frees its memory until the next
load. Measured on a Pixel 8a (Android 16, LiteRT-LM 0.16.1): 10.5 tokens/s decode on the CPU
backend and 13.8 on the GPU backend, 0.7 s to the first token, 1928 MB of process memory
while loaded and 89 MB after Release, 6 to 9 s to load the model and 1.4 s to reload it.
Model and code are Apache-2.0. Everything below was run on 2026-09-05; the same facts in
machine-readable form are in [`recipe.json`](recipe.json).

The model is [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) as the
`.litertlm` bundle Google publishes in
[litert-community/Qwen2.5-1.5B-Instruct](https://huggingface.co/litert-community/Qwen2.5-1.5B-Instruct)
(not gated, 8-bit weights, 4096-token context). The runtime is
[LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM), Google AI Edge's on-device LLM runtime;
the same bundle runs on iOS, macOS, Linux and Windows through the same project.

## 1. Dependency

`app/build.gradle.kts`:

```kotlin
android {
  defaultConfig { minSdk = 24 }   // the floor the litertlm-android AAR declares
}
dependencies {
  implementation("com.google.ai.edge.litertlm:litertlm-android:0.16.1")
  implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.11.0")
}
```

Both lines are needed. The coroutines pin is not optional: the AAR's POM asks for an older
coroutines version than its bytecode calls, and without the pin replies crash with
`NoSuchMethodError` at the moment streaming completes. Do not add the standalone
`org.jetbrains.kotlin.android` plugin on AGP 9 or newer; Kotlin is built in and applying it is a
hard error. Repositories: `google()` and `mavenCentral()`. Verified toolchain: AGP 9.3.1,
Gradle 9.7.0, compileSdk 36, JDK 17.

## 2. Copy two files

| file | what it is |
|---|---|
| [`ChatEngine.kt`](app/src/main/kotlin/io/github/johnrocky/llmchat/ChatEngine.kt) | every LiteRT-LM call: `initialize()`, `send(prompt): Flow<String>`, `cancel()`, `close()`, plus the chat history (`turns`) that survives a cancel and a reload. No Android UI types. |
| [`ModelProvisioner.kt`](app/src/main/kotlin/io/github/johnrocky/llmchat/ModelProvisioner.kt) | puts the model file in `filesDir/models/`, downloading it once with the sha256 checked while streaming. |

Change the `package` line of each; keep the comments, they explain the non-obvious parts.
[`MainActivity.kt`](app/src/main/kotlin/io/github/johnrocky/llmchat/MainActivity.kt) shows how a
plain Activity drives them (Send, Stop, Release model); it is a reference, not a file to copy.

## 3. Get the model

| | |
|---|---|
| file | `Qwen2.5-1.5B-Instruct_multi-prefill-seq_q8_ekv4096.litertlm` |
| URL | `https://huggingface.co/litert-community/Qwen2.5-1.5B-Instruct/resolve/main/Qwen2.5-1.5B-Instruct_multi-prefill-seq_q8_ekv4096.litertlm` |
| sha256 | `faa60663b333290c1496c499828b21d3e3254a788cacd8cce917ce0f761a2dc9` |
| size | 1,597,931,520 bytes |
| license | Apache-2.0 (the card's license field) |

One delivery pattern: the app owns `filesDir/models/<file>` and fills it by download on first
launch. `ModelProvisioner.provision(context, url, sha256, bytes)` streams the download into a
`.part` file, checks the sha256 and the size, and renames only when both match, so a truncated
download is never loaded. Put the URL, hash and size in `BuildConfig` fields (see
[`app/build.gradle.kts`](app/build.gradle.kts), which reads them from `recipe.json`) or as
constants. The manifest needs `INTERNET` for that download only; inference makes no network call.

During development, skip the 1.6 GB download over Wi-Fi. Install the app first (any launch or
`./gradlew installDebug`), then push the file straight into its external files directory:

```sh
shasum -a 256 Qwen2.5-1.5B-Instruct_multi-prefill-seq_q8_ekv4096.litertlm   # must print faa60663...
adb push Qwen2.5-1.5B-Instruct_multi-prefill-seq_q8_ekv4096.litertlm \
  /sdcard/Android/data/<applicationId>/files/
```

The provisioner uses that copy in place when its size matches. Do not `adb shell mkdir` a
subdirectory for it: a directory created by the shell under `Android/data` belongs to the shell
user, the app cannot enter it, and the provisioner then falls back to the download without saying
so (that is how one of today's runs ended up downloading next to a pushed copy). Never bundle the
file into the APK and never commit it.

## 4. Use it

```kotlin
val engine = ChatEngine(modelFile.absolutePath, cacheDir = context.cacheDir.path)  // Backend.CPU()
engine.initialize()                                     // suspend; seconds, on Dispatchers.IO
engine.send("In one sentence, what is the capital of France?")
    .catch { e -> showError(e) }
    .collect { chunk -> transcript.append(chunk) }    // chunks are incremental: append
```

Turns share one conversation, so the model sees earlier turns. The CPU backend needs nothing
else and runs on every supported device. For the GPU backend pass `Backend.GPU()` and add the two
`<uses-native-library>` entries from [`AndroidManifest.xml`](app/src/main/AndroidManifest.xml)
(`libOpenCL.so`, `libvndksupport.so`, both `required="false"`); if GPU initialization fails, show
the error instead of silently falling back, or a slow path looks like a working one.

## 5. Stop and release

**Stop.** Cancel the coroutine that collects `send(...)`, and generation stops on the native side
as well: `ChatEngine.send` calls the runtime's `cancelProcess()` from `onCompletion` when the
collector is cancelled. This matters because the runtime's own `sendMessageAsync` flow has an empty
`awaitClose`, so a cancelled collector alone would leave the model decoding to the end of its
reply on a background thread. Alternatively call `engine.cancel()` from anywhere (a Stop button):
the flow then completes normally with the chunks delivered so far.

After a cancel, the next `send(...)` still works, but not on the same runtime object. LiteRT-LM
0.16 documents that a session is not reusable after `cancelProcess()` ("leaves the session state
poisoned", `runtime/core/session_advanced.h`; rollback is an open TODO), and in this test the
next reply on the cancelled conversation came back empty. `ChatEngine` therefore keeps the chat
history itself (completed user and model turns) and, on the next `send(...)` after a cancel,
closes the runtime conversation and opens a new one seeded with that history. The cost is one
prefill of the chat so far, which shows up as a longer time to first chunk on that turn; the
numbers are in section 6. From the app's side nothing changes: same `send(...)`, same chat.

The cancelled turn itself is not part of that history. Keeping the cut-off reply as a model turn
was tried first: asked "Say OK." right after a cancelled 400-word story, the model returned 2,717
characters of the story instead, byte-identical in two runs. The runtime's own cancel path drops
the turn too. Show the partial text in your transcript if you like; the model does not see it
again.

**Release.** `engine.close()` closes the conversation and the engine, in that order, and frees
the model's memory; the chat history stays in the `ChatEngine` instance. It is safe while a reply
is streaming: `close()` cancels the reply first, because deleting the native conversation waits
for the work in flight (`~SessionAdvanced` "will wait for all tasks to be done"), so without the
cancel it would block until the reply ends. `initialize()` on the same instance loads the model
again and continues the chat; the compile cache in `cacheDir` makes the second load faster. Do
this when the app goes to the background for long, and always in `onDestroy`.

## 6. Verify the integration

```sh
./gradlew :app:connectedDebugAndroidTest -Pandroid.injected.androidTest.leaveApksInstalledAfterRun=true
# GPU backend: add -Pandroid.testInstrumentationRunnerArguments.backend=gpu
# faster repeat runs, after the first install: adb push <model file> /sdcard/Android/data/io.github.johnrocky.llmchat/files/
```

On the first run the test downloads the model through the same `ModelProvisioner` path an app
uses (about 3 minutes on Wi-Fi), which is how the download path gets exercised. The
`leaveApksInstalledAfterRun` flag matters: without it Gradle uninstalls the app after the run, and
the uninstall deletes the downloaded model, a pushed copy, and the runtime's cache with it.

[`ChatIntegrationTest`](app/src/androidTest/kotlin/io/github/johnrocky/llmchat/ChatIntegrationTest.kt)
runs five checks against the real model and logs one `RESULT` line per check under the logcat tag
`recipe` (`adb logcat -s recipe`), plus one `PROVISION` line saying where the model came from.
Expected on a Pixel 8a (Android 16, build CP1A.260505.005), LiteRT-LM 0.16.1, 2026-09-05, phone idle
(nothing else in `top`), thermal status 1. The lines are trimmed to the values; the full lines also carry
the device, backend and runtime version.

CPU backend (the default):

```
PROVISION via=pushed ms=9 bytes=1597931520
RESULT check=turn load_ms=8794 chunks=7 chars=31 first_chunk_ms=909 prefill_tok_s=55.45 decode_tok_s=8.90 ttft_s=0.67 reply="The capital of France is Paris." second_turn_chars=31
RESULT check=throughput prompt="Explain in five sentences why the sky is blue." runs=3 decode_tokens=113/113/122 decode_tok_s=10.48/10.54/10.26 decode_tok_s_median=10.48 prefill_tok_s=60.29/55.28/50.75 thermal_status=1->1
RESULT check=cancel_collector chunks_before_cancel=10 cpu_ms_generating=2020/502ms cpu_ms_after_cancel=80/1507ms next_turn_first_chunk_ms=1578 turns=4 intro_reply="Hello Alice! How can I help you today?" next_turn_reply=Alice
RESULT check=cancel_explicit chunks=6 flow_completed_ms=2219 cpu_ms_after_cancel=10/1506ms next_turn_first_chunk_ms=1099 turns=2 partial="1, 2, " next_turn_head=OK.
RESULT check=release load1_ms=1381 pss_loaded_kb=1975121 pss_released_kb=91633 load2_ms=1442 reply_chars_after_reload=31 turns_after_reload=4
RESULT check=close_during_generation chunks_at_close=6 close_ms=535 cpu_ms_after_close=30/1509ms reload_ms=1154 next_turn_head=OK.
run finished: 5 tests, 0 failed
```

GPU backend (`-Pandroid.testInstrumentationRunnerArguments.backend=gpu`):

```
PROVISION via=pushed ms=10 bytes=1597931520
RESULT check=turn load_ms=6691 chunks=7 chars=31 first_chunk_ms=1448 prefill_tok_s=96.97 decode_tok_s=5.40 ttft_s=0.50 reply="The capital of France is Paris." second_turn_chars=31
RESULT check=throughput prompt="Explain in five sentences why the sky is blue." runs=3 decode_tokens=30/37/39 decode_tok_s=13.28/13.81/13.80 decode_tok_s_median=13.80 prefill_tok_s=74.61/70.22/69.80 thermal_status=1->1
RESULT check=cancel_collector chunks_before_cancel=13 cpu_ms_generating=390/504ms cpu_ms_after_cancel=60/1512ms next_turn_first_chunk_ms=929 turns=4 intro_reply="Hello Alice! It's nice to meet you. How can I assist you today?" next_turn_reply=Alice
RESULT check=cancel_explicit chunks=6 flow_completed_ms=1830 cpu_ms_after_cancel=70/1511ms next_turn_first_chunk_ms=714 turns=2 partial="1, 2, " next_turn_head=OK.
RESULT check=release load1_ms=6909 pss_loaded_kb=2647531 pss_released_kb=492268 load2_ms=5483 reply_chars_after_reload=31 turns_after_reload=4
RESULT check=close_during_generation chunks_at_close=6 close_ms=696 cpu_ms_after_close=220/1510ms reload_ms=4610 next_turn_head=OK.
run finished: 5 tests, 0 failed
```

On the first run after install, when the model is downloaded and the runtime builds its weight cache,
the same test showed `PROVISION via=download ms=180871` and `load_ms=6450` (CPU); the first-ever GPU load
on this phone, when the OpenCL kernels are built, took 62 to 67 s in two earlier runs.

What each check asserts:

| check | asserts |
|---|---|
| `turn` | a fixed prompt streams a non-blank reply in more than one chunk; a second turn in the same conversation is non-blank |
| `cancel_collector` | after cancelling the collecting coroutine, no further chunk arrives and the process's CPU time over the next 1.5 s stays under 400 ms (while generating it is measured as the control); the next prompt is answered |
| `cancel_explicit` | `cancel()` from inside the collector makes the flow complete normally with the partial text; same CPU check; the next prompt is answered |
| `release` | `close()` then `initialize()` on the same instance answers the prompt again with the chat history kept; PSS before and after `close()` is logged |
| `close_during_generation` | `close()` while a reply is streaming returns in under 10 s, the process is idle over the next 1.5 s, and `initialize()` plus the next prompt work |
| `throughput` | three turns of a fixed prompt; the runtime's own prefill and decode tokens/s per turn, with the thermal status before and after |

Latency, tokens per second and memory are logged conditions, not assertions. Take the throughput
numbers only with nothing else running on the phone (`adb shell top` first) and at thermal status
0 or 1; a foreign workload on the same cores halves them, which is how one afternoon's runs went
from 10 to 2.7 decode tokens/s before the cause was found.

## 7. Verified / unverified

Verified on 2026-09-05 with the command in section 6, on one phone: Pixel 8a (Tensor G3), Android 16
build CP1A.260505.005 (SDK 36), USB power, screen on, nothing else running, thermal status 1 before and
after each run.

| backend | LiteRT-LM | decode tokens/s (median of 3 turns) | prefill tokens/s | first token | model load / reload | process memory loaded, after Release | CPU time in the 1.5 s after a cancel | `close()` during a reply |
|---|---|---|---|---|---|---|---|---|
| CPU | 0.16.1 | 10.48 (113/113/122 tokens per turn) | 55.4 | 0.67 s | 8.8 s / 1.4 s | 1928 MB, 89 MB | 80 ms (generating: 2020 ms per 0.5 s) | 535 ms |
| GPU | 0.16.1 | 13.80 (30/37/39 tokens per turn) | 71.5 | 0.50 s | 6.7 s / 5.5 s | 2585 MB, 480 MB | 60 ms (generating: 390 ms per 0.5 s) | 696 ms |
| CPU | 0.17.0, metadata check skipped | 10.20 (92/110/110 tokens per turn) | 42.9 | 0.60 s | 13.3 s / 1.6 s | 1927 MB, 87 MB | 10 ms (generating: 1790 ms per 0.5 s) | 597 ms |

Also verified: the download path (first run after install: 1,597,931,520 bytes in 181 s on Wi-Fi, sha256
checked while streaming), the pushed copy in the app's external files dir, the chat history surviving a
cancel (a name given before the cancelled turn is recalled after it) and a Release plus reload (4 turns
kept), and a prompt after a cancel getting a fresh short answer ("OK.").

Facts around the table:

- The runtime's own numbers vary with heat and neighbours. The same CPU configuration gave 10.57 tokens/s
  at thermal status 0 and 10.48 at status 1, and 2.7 while another benchmark was using four cores of the
  same phone. Check `adb shell top` and `dumpsys thermalservice` before quoting a number.
- The GPU backend answered the same prompts with shorter replies (30 to 39 decode tokens against 113 to
  122 on the CPU); the cause was not investigated. Its process memory after Release stays at
  480 MB, most of it the GPU driver.
- litertlm-android 0.17.0 is on Google Maven (2026-09-04; no GitHub release on 2026-09-05) but ships
  Kotlin 2.4 metadata, which the Kotlin built into AGP 9.3.1 (2.2) refuses: "Module was compiled with an
  incompatible version of Kotlin. The binary version of its metadata is 2.4.0, expected version is 2.2.0".
  With `-PskipKotlinMetadataCheck=true` (a diagnostic switch in `app/build.gradle.kts`) it compiled and
  passed all five checks; the recipe stays on 0.16.1 until a toolchain with Kotlin 2.4 support is verified.

Not verified:

- Android emulator: not run (the CPU backend may work there; the GPU backend will not).
- Any device other than the Pixel 8a above (Samsung Galaxy / Adreno, MediaTek, other Pixels), and
  Android versions other than 16.
- The f32 bundle in the same repository (6.2 GB); only the q8 file was used.
- Tool calling, images, audio, thinking mode, LoRA: not touched by this recipe.
- Conversations longer than the 4096-token KV cache of this bundle.
- Download over a metered or interrupted connection: the sha256 check rejects a truncated file; resuming
  is not implemented.
- Galaxy S26 rows for the same bundle exist through the litert-lm CLI
  ([apple-silicon-llm-bench](https://github.com/john-rocky/apple-silicon-llm-bench/blob/main/results/android/litertlm-qwen2.5-1.5b-mac-galaxy-s26.md)),
  taken with a different harness, not with this test.

## 8. Provenance

- Converted and verified by: litert-community (Google AI Edge) published the bundle; integration and verification by john-rocky
- Recipe: https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md
- Measurements: section 7 above (Pixel 8a, 2026-09-05)
- Commit: john-rocky/on-device-recipes@086a791 (the recipe, the files and the device rows above)
- Maintained at: https://github.com/john-rocky/on-device-recipes/issues

Last verified: 2026-09-05
