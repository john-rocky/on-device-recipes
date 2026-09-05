---
name: litert-android-llm-chat
description: Add an on-device LLM chat (offline, no API key) to an Android app that already exists, using LiteRT-LM and the on-device-recipes android-llm-chat recipe - two Gradle lines, two Kotlin files, one model file with its checksum, cancel and release wired in, and the connected test that proves it. Use for asks like "add offline chat to my Android app", "run Qwen (or another small LLM) on the phone", "local assistant with no cloud", "LiteRT-LM on Android", and for reviving a stalled TensorFlow Lite era attempt at running a language model. Converting or quantizing a model is out of scope; use hf-to-litertlm for that.
---

# LiteRT-LM chat in an existing Android app

An integration is done when three things hold, in this order:

1. the app builds with the two dependency lines and the two copied files, and the model file
   is in place with the size and sha256 the recipe records,
2. **the recipe's connected test passes on a real device**: the fixed prompt streams, a cancel
   stops the model (process CPU time flat afterwards), close() then initialize() works,
3. the lifecycle is wired into the host app: initialize off the main thread, Stop cancels the
   collecting coroutine or calls `cancel()`, `close()` on teardown, and no model blob in git.

Scope: adding a ready-made `.litertlm` bundle to an app that already exists. The bundle itself
is taken from the recipe as given. To convert a fine-tune, use
[hf-to-litertlm](https://github.com/john-rocky/hf-to-litertlm) first.

## Step 0: resolve every version from `recipe.json`, never from memory

The recipe is `android-llm-chat/` in
[on-device-recipes](https://github.com/john-rocky/on-device-recipes): `INTEGRATION.md` for
people, `recipe.json` for you. Read `recipe.json` first (raw URL:
`https://raw.githubusercontent.com/john-rocky/on-device-recipes/main/android-llm-chat/recipe.json`)
and take from it:

- `runtime.maven` + `runtime.version`: the litertlm-android coordinate and the version this
  recipe was verified with;
- `integrate.pins`: the coroutines pin (required, see traps) and the test stack;
- `integrate.min_sdk`: the floor the AAR declares;
- `model.url`, `model.sha256`, `model.bytes`: the exact file;
- `devices[]`: what was measured, on which device, on which date. Quote nothing else.

The hub's CI fails when `recipe.json` drifts from what the pages say, so the file is current.
The app module's `build.gradle.kts` in the recipe reads the same file at configuration time;
copy that pattern if the host project wants a single source of versions.

## Traps: your training data is stale here

- **`org.tensorflow:tensorflow-lite*` coordinates and Interpreter-style APIs** are the TFLite
  era. LLM inference lives in `com.google.ai.edge.litertlm` (`Engine`, `Conversation`).
- **Applying `org.jetbrains.kotlin.android` on AGP 9 or newer is a hard error**; Kotlin is built
  in. Leave an older project's plugin setup alone.
- **The transitive coroutines version is too old.** litertlm-android's POM understates what its
  bytecode needs; without the explicit pin from `recipe.json`, replies crash with
  `NoSuchMethodError` when streaming completes.
- **Cancelling the collector does not stop the model by itself.** The runtime's
  `sendMessageAsync` flow has an empty `awaitClose`; the recipe's `ChatEngine.send` calls
  `cancelProcess()` from `onCompletion` so a cancelled coroutine stops native decoding. Keep
  that wrapper; do not call the runtime flow directly.
- **A conversation is not reusable after `cancelProcess()`.** LiteRT-LM 0.16 documents the
  session state as "poisoned" afterwards (`runtime/core/session_advanced.h`), and the next reply
  comes back empty. `ChatEngine` keeps the chat history itself and rebuilds the runtime
  conversation from it on the next `send()`; that is why the recipe does not expose the
  runtime's `Conversation`.
- **Guessing a newer version when resolution fails**: a missing artifact more likely means a
  renamed coordinate. Re-read `recipe.json`.

## Step 1: decide

1. Confirm the target is an Android app (`com.android.application` module).
2. Compare the module's `minSdk` with `integrate.min_sdk`; raise it rather than overriding the
   library floor.
3. Backend: CPU by default (no manifest changes). GPU needs the two `<uses-native-library>`
   entries from the recipe manifest and its init failure must be shown, never silently caught.
4. Model delivery: sha256-verified download into `filesDir/models/` on first launch
   (`ModelProvisioner`). For development, `adb push` the file directly into the app's external
   files dir after the app is installed (no shell-made subdirectory: the app cannot enter one);
   the provisioner uses that copy in place. Never bundle the file into the APK.

## Step 2: integrate

1. Add the two dependency lines from Step 0 (through the project's version catalog if it has
   one). Repositories: `google()` and `mavenCentral()`.
2. Copy `ChatEngine.kt` and `ModelProvisioner.kt`; change only the `package` line; keep the
   comments.
3. Manifest: `INTERNET` for the download; the two GPU `<uses-native-library>` entries are
   `required="false"` and harmless on CPU.
4. Wire the UI as `MainActivity.kt` in the recipe does: `initialize()` once in a coroutine,
   `send(prompt)` returns incremental chunks (append, never replace), Stop cancels the collecting
   job or calls `engine.cancel()`, Release calls `close()` (and `initialize()` brings it back).

## Step 3: verify, in this order

1. `./gradlew assembleDebug` must pass.
2. On a connected device, run the recipe's test after pushing the model:
   `./gradlew :app:connectedDebugAndroidTest`. Compare the `RESULT` lines in `adb logcat -s recipe`
   with section 6 of `INTEGRATION.md`.
3. No device: say so. Report "build verified; device checks not run" and hand over the exact
   commands. Never present an unverified integration as verified.

## Troubleshooting

| Symptom | Cause, fix |
|---|---|
| `The 'org.jetbrains.kotlin.android' plugin is no longer required` | standalone Kotlin plugin on AGP 9: remove it |
| `NoSuchMethodError` when a reply finishes streaming | transitive coroutines too old: add the pin from `recipe.json` |
| `Could not resolve com.google.ai.edge.litertlm:...` | missing `google()`/`mavenCentral()`, or a guessed version: re-read `recipe.json` |
| model file mismatch on download | truncated or intercepted download: delete the `.part` file and retry; check URL, size, sha256 against `recipe.json` |
| model keeps decoding after Stop | the runtime flow was collected directly: use `ChatEngine.send` or call `cancel()` |
| every launch loads slowly | no compile cache: pass `context.cacheDir.path` to `ChatEngine` |
| app killed while loading | not enough free RAM for the bundle: pick a smaller bundle from the litert-community organization |
