package io.github.johnrocky.llmchat

import android.content.Context
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Puts the model file where [ChatEngine] can load it. One delivery pattern: the app owns
 * `filesDir/models/<file>`, filled by a sha256-verified download on first launch.
 *
 * Two shortcuts keep the inner loop fast and are checked first, in this order:
 * 1. A developer-pushed copy directly in the app's external files dir (after the app is installed):
 *    `adb push <file> /sdcard/Android/data/<applicationId>/files/`
 *    Used in place (no copy). Its size must match [expectedBytes]; the hash is not recomputed,
 *    so verify the file on the host before pushing (`shasum -a 256 <file>`). Do not create a
 *    subdirectory from the shell for it: a directory made by `adb shell mkdir` under
 *    Android/data belongs to the shell user and the app cannot enter it (measured: the
 *    provisioner then silently falls back to the download).
 * 2. A previously downloaded copy in `filesDir/models/`, also size-checked.
 *
 * The sha256 is verified while the download streams, into a `.part` file that is renamed only
 * when the hash matches, so a truncated download is never mistaken for the model.
 */
object ModelProvisioner {

    suspend fun provision(
        context: Context,
        url: String,
        sha256: String,
        expectedBytes: Long,
        onProgress: (message: String) -> Unit,
    ): File = withContext(Dispatchers.IO) {
        val fileName = url.substringAfterLast('/')

        val pushed = context.getExternalFilesDir(null)?.let { File(it, fileName) }
        if (pushed != null && pushed.canRead() && pushed.length() == expectedBytes) {
            return@withContext pushed
        }

        val target = File(context.filesDir, "models/$fileName")
        if (target.exists() && target.length() == expectedBytes) {
            return@withContext target
        }

        download(url, sha256, expectedBytes, target, onProgress)
        target
    }

    private fun download(
        url: String,
        expectedSha256: String,
        expectedBytes: Long,
        target: File,
        onProgress: (message: String) -> Unit,
    ) {
        target.parentFile?.mkdirs()
        val tmp = File(target.parentFile, "${target.name}.part")
        val digest = MessageDigest.getInstance("SHA-256")
        val connection = URL(url).openConnection() as HttpURLConnection
        var read = 0L
        try {
            connection.instanceFollowRedirects = true
            if (connection.responseCode !in 200..299) {
                throw IOException("GET $url -> HTTP ${connection.responseCode}")
            }
            connection.inputStream.use { input ->
                tmp.outputStream().use { output ->
                    val buffer = ByteArray(1 shl 16)
                    while (true) {
                        val n = input.read(buffer)
                        if (n < 0) break
                        output.write(buffer, 0, n)
                        digest.update(buffer, 0, n)
                        read += n
                        onProgress("Downloading model: ${read * 100 / expectedBytes}%")
                    }
                }
            }
        } finally {
            connection.disconnect()
        }
        val actual = digest.digest().joinToString("") { "%02x".format(it) }
        if (read != expectedBytes || !actual.equals(expectedSha256, ignoreCase = true)) {
            tmp.delete()
            throw IOException(
                "model file mismatch for $url: got $read bytes / sha256 $actual, " +
                    "expected $expectedBytes bytes / sha256 $expectedSha256"
            )
        }
        if (!tmp.renameTo(target)) {
            tmp.delete()
            throw IOException("could not move ${tmp.name} into place")
        }
    }
}
