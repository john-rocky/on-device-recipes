import groovy.json.JsonSlurper

// No org.jetbrains.kotlin.android here: Kotlin support is built into AGP since 9.0,
// and applying the standalone plugin is a configuration error on this toolchain.
plugins {
    id("com.android.application")
}

// ../recipe.json is the single source of truth for the runtime version, the pinned
// dependency versions and the model file. Edit it, not the numbers below.
@Suppress("UNCHECKED_CAST")
val recipe = JsonSlurper().parse(rootProject.file("recipe.json")) as Map<String, Any>
@Suppress("UNCHECKED_CAST")
val model = recipe["model"] as Map<String, Any>
@Suppress("UNCHECKED_CAST")
val runtime = recipe["runtime"] as Map<String, Any>
@Suppress("UNCHECKED_CAST")
val integrate = recipe["integrate"] as Map<String, Any>
@Suppress("UNCHECKED_CAST")
val pins = integrate["pins"] as Map<String, String>

// `./gradlew ... -PlitertlmVersion=0.17.0` re-runs the same verification against another
// LiteRT-LM release without touching recipe.json.
val litertlmVersion = providers.gradleProperty("litertlmVersion").getOrElse(runtime["version"] as String)

android {
    namespace = "io.github.johnrocky.llmchat"
    compileSdk = 36

    defaultConfig {
        applicationId = "io.github.johnrocky.llmchat"
        minSdk = (integrate["min_sdk"] as Number).toInt()
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        buildConfigField("String", "MODEL_URL", "\"${model["url"]}\"")
        buildConfigField("String", "MODEL_SHA256", "\"${model["sha256"]}\"")
        buildConfigField("long", "MODEL_BYTES", "${model["bytes"]}L")
        buildConfigField("String", "LITERTLM_VERSION", "\"$litertlmVersion\"")
    }

    buildFeatures {
        buildConfig = true
    }

    // litertlm-android 0.17.0 ships Kotlin 2.4 metadata, which the Kotlin built into AGP 9.3.1
    // (2.2) refuses. `-PskipKotlinMetadataCheck=true` lets a re-gate compile anyway; it is a
    // diagnostic switch, not a supported configuration.
    if (providers.gradleProperty("skipKotlinMetadataCheck").isPresent) {
        kotlin {
            compilerOptions {
                freeCompilerArgs.add("-Xskip-metadata-version-check")
            }
        }
    }
}

dependencies {
    implementation("${runtime["maven"]}:$litertlmVersion")
    // Explicit pin required: litertlm-android's POM understates the coroutines version its
    // bytecode needs; without it, replies crash with NoSuchMethodError when streaming completes.
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:${pins["org.jetbrains.kotlinx:kotlinx-coroutines-android"]}")

    androidTestImplementation("androidx.test:runner:${pins["androidx.test:runner"]}")
    androidTestImplementation("androidx.test.ext:junit:${pins["androidx.test.ext:junit"]}")
    androidTestImplementation("junit:junit:${pins["junit:junit"]}")
}
