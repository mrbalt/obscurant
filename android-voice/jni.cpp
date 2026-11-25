// Minimal Java bridge to whisper.cpp for the Obscurant voice assistant. Audio stays in memory.
#include <jni.h>
#include <string>
#include "whisper.h"

static void quiet(enum ggml_log_level, const char *, void *) {}

extern "C" JNIEXPORT jlong JNICALL
Java_org_mozilla_fenix_voice_WhisperEngine_nativeInit(JNIEnv *env, jobject, jstring path) {
    whisper_log_set(quiet, nullptr);
    const char *file = env->GetStringUTFChars(path, nullptr);
    whisper_context_params params = whisper_context_default_params();
    params.use_gpu = false;
    whisper_context *context = whisper_init_from_file_with_params(file, params);
    env->ReleaseStringUTFChars(path, file);
    return reinterpret_cast<jlong>(context);
}

extern "C" JNIEXPORT jbyteArray JNICALL
Java_org_mozilla_fenix_voice_WhisperEngine_nativeTranscribe(
        JNIEnv *env, jobject, jlong handle, jfloatArray audio, jstring prompt, jint threads) {
    whisper_context *context = reinterpret_cast<whisper_context *>(handle);
    const jsize count = env->GetArrayLength(audio);
    jfloat *samples = env->GetFloatArrayElements(audio, nullptr);
    const char *hint = env->GetStringUTFChars(prompt, nullptr);

    // Same choices as the desktop helper: greedy, no fallback, a short encoder window.
    whisper_full_params params = whisper_full_default_params(WHISPER_SAMPLING_GREEDY);
    params.n_threads = threads;
    params.language = "en";
    params.initial_prompt = hint;
    params.no_context = true;
    params.no_timestamps = true;
    params.single_segment = true;
    params.temperature_inc = 0.0f;
    params.audio_ctx = 768;
    params.print_progress = false;
    params.print_realtime = false;
    params.print_timestamps = false;
    params.print_special = false;

    std::string text;
    if (whisper_full(context, params, samples, count) == 0) {
        for (int i = 0; i < whisper_full_n_segments(context); i++) {
            text += whisper_full_get_segment_text(context, i);
        }
    }
    env->ReleaseStringUTFChars(prompt, hint);
    env->ReleaseFloatArrayElements(audio, samples, JNI_ABORT);
    jbyteArray out = env->NewByteArray(static_cast<jsize>(text.size()));
    env->SetByteArrayRegion(out, 0, static_cast<jsize>(text.size()), reinterpret_cast<const jbyte *>(text.data()));
    return out;
}

extern "C" JNIEXPORT void JNICALL
Java_org_mozilla_fenix_voice_WhisperEngine_nativeFree(JNIEnv *, jobject, jlong handle) {
    whisper_free(reinterpret_cast<whisper_context *>(handle));
}
