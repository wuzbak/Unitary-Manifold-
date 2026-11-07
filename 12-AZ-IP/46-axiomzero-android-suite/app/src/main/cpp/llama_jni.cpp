#include <jni.h>

#include "llama.h"

#include <algorithm>
#include <atomic>
#include <cstdint>
#include <string>
#include <thread>
#include <vector>
#include <mutex>

namespace {

std::atomic_bool cancel_load{false};
std::once_flag backend_init_once;

bool continue_loading(float, void *) {
    return !cancel_load.load();
}

bool abort_generation(void *user_data) {
    return static_cast<std::atomic_bool *>(user_data)->load();
}

struct Session {
    llama_model *model = nullptr;
    llama_context *context = nullptr;
    uint32_t context_tokens = 0;
    std::atomic_bool cancelled{false};

    ~Session() {
        if (context != nullptr) {
            llama_free(context);
        }
        if (model != nullptr) {
            llama_model_free(model);
        }
    }
};

std::string to_string(JNIEnv *env, jstring input) {
    if (input == nullptr) {
        return {};
    }
    const jchar *chars = env->GetStringChars(input, nullptr);
    if (chars == nullptr) {
        return {};
    }
    const jsize length = env->GetStringLength(input);
    std::string result;
    for (jsize index = 0; index < length; ++index) {
        uint32_t codepoint = chars[index];
        if (codepoint >= 0xd800 && codepoint <= 0xdbff && index + 1 < length) {
            const uint32_t low = chars[index + 1];
            if (low >= 0xdc00 && low <= 0xdfff) {
                codepoint = 0x10000 + ((codepoint - 0xd800) << 10) + (low - 0xdc00);
                ++index;
            }
        }
        if (codepoint >= 0xd800 && codepoint <= 0xdfff) {
            codepoint = 0xfffd;
        }
        if (codepoint <= 0x7f) {
            result.push_back(static_cast<char>(codepoint));
        } else if (codepoint <= 0x7ff) {
            result.push_back(static_cast<char>(0xc0 | (codepoint >> 6)));
            result.push_back(static_cast<char>(0x80 | (codepoint & 0x3f)));
        } else if (codepoint <= 0xffff) {
            result.push_back(static_cast<char>(0xe0 | (codepoint >> 12)));
            result.push_back(static_cast<char>(0x80 | ((codepoint >> 6) & 0x3f)));
            result.push_back(static_cast<char>(0x80 | (codepoint & 0x3f)));
        } else {
            result.push_back(static_cast<char>(0xf0 | (codepoint >> 18)));
            result.push_back(static_cast<char>(0x80 | ((codepoint >> 12) & 0x3f)));
            result.push_back(static_cast<char>(0x80 | ((codepoint >> 6) & 0x3f)));
            result.push_back(static_cast<char>(0x80 | (codepoint & 0x3f)));
        }
    }
    env->ReleaseStringChars(input, chars);
    return result;
}

void append_utf16(std::vector<jchar> &output, uint32_t codepoint) {
    if (codepoint <= 0xffff) {
        output.push_back(static_cast<jchar>(codepoint));
    } else {
        codepoint -= 0x10000;
        output.push_back(static_cast<jchar>(0xd800 + (codepoint >> 10)));
        output.push_back(static_cast<jchar>(0xdc00 + (codepoint & 0x3ff)));
    }
}

jstring new_string_from_utf8(JNIEnv *env, const std::string &input) {
    std::vector<jchar> output;
    output.reserve(input.size());
    size_t index = 0;
    while (index < input.size()) {
        const auto first = static_cast<uint8_t>(input[index]);
        uint32_t codepoint = 0xfffd;
        size_t length = 1;
        if (first < 0x80) {
            codepoint = first;
        } else if ((first & 0xe0) == 0xc0 && index + 1 < input.size()) {
            const auto next = static_cast<uint8_t>(input[index + 1]);
            if ((next & 0xc0) == 0x80) {
                codepoint = ((first & 0x1f) << 6) | (next & 0x3f);
                length = 2;
                if (codepoint < 0x80) codepoint = 0xfffd;
            }
        } else if ((first & 0xf0) == 0xe0 && index + 2 < input.size()) {
            const auto next = static_cast<uint8_t>(input[index + 1]);
            const auto last = static_cast<uint8_t>(input[index + 2]);
            if ((next & 0xc0) == 0x80 && (last & 0xc0) == 0x80) {
                codepoint = ((first & 0x0f) << 12) | ((next & 0x3f) << 6) | (last & 0x3f);
                length = 3;
                if (codepoint < 0x800 || (codepoint >= 0xd800 && codepoint <= 0xdfff)) {
                    codepoint = 0xfffd;
                }
            }
        } else if ((first & 0xf8) == 0xf0 && index + 3 < input.size()) {
            const auto next = static_cast<uint8_t>(input[index + 1]);
            const auto third = static_cast<uint8_t>(input[index + 2]);
            const auto last = static_cast<uint8_t>(input[index + 3]);
            if ((next & 0xc0) == 0x80 && (third & 0xc0) == 0x80 && (last & 0xc0) == 0x80) {
                codepoint = ((first & 0x07) << 18) | ((next & 0x3f) << 12) |
                    ((third & 0x3f) << 6) | (last & 0x3f);
                length = 4;
                if (codepoint < 0x10000 || codepoint > 0x10ffff) codepoint = 0xfffd;
            }
        }
        append_utf16(output, codepoint);
        index += length;
    }
    const jchar empty = 0;
    return env->NewString(
        output.empty() ? &empty : output.data(), static_cast<jsize>(output.size()));
}

jstring error(JNIEnv *env, const char *message) {
    return env->NewStringUTF(message);
}

}  // namespace

extern "C" JNIEXPORT jstring JNICALL
Java_com_axiomzero_androidsuite_LocalModelRuntime_nativeVersion(JNIEnv *env, jobject) {
    return env->NewStringUTF(llama_version());
}

extern "C" JNIEXPORT jlong JNICALL
Java_com_axiomzero_androidsuite_LocalModelRuntime_nativeLoad(
    JNIEnv *env, jobject, jstring path, jint context_tokens) {
    const std::string model_path = to_string(env, path);
    if (model_path.empty() || context_tokens < 512 || context_tokens > 4096) {
        return 0;
    }

    cancel_load.store(false);
    std::call_once(backend_init_once, llama_backend_init);
    auto model_params = llama_model_default_params();
    model_params.n_gpu_layers = 0;
    model_params.progress_callback = continue_loading;
    auto session = new Session();
    session->model = llama_model_load_from_file(model_path.c_str(), model_params);
    if (session->model == nullptr || cancel_load.load()) {
        delete session;
        return 0;
    }

    auto context_params = llama_context_default_params();
    context_params.n_ctx = static_cast<uint32_t>(context_tokens);
    context_params.n_batch = std::min<uint32_t>(512, context_params.n_ctx);
    context_params.n_ubatch = context_params.n_batch;
    const int32_t threads = static_cast<int32_t>(
        std::clamp(std::thread::hardware_concurrency(), 1u, 4u));
    context_params.n_threads = threads;
    context_params.n_threads_batch = threads;
    context_params.abort_callback = abort_generation;
    context_params.abort_callback_data = &session->cancelled;
    session->context = llama_init_from_model(session->model, context_params);
    if (session->context == nullptr) {
        delete session;
        return 0;
    }
    session->context_tokens = context_params.n_ctx;
    return reinterpret_cast<jlong>(session);
}

extern "C" JNIEXPORT void JNICALL
Java_com_axiomzero_androidsuite_LocalModelRuntime_nativeCancelLoad(JNIEnv *, jobject) {
    cancel_load.store(true);
}

extern "C" JNIEXPORT jlong JNICALL
Java_com_axiomzero_androidsuite_LocalModelRuntime_nativeCreateCancellationProbe(JNIEnv *, jobject) {
    return reinterpret_cast<jlong>(new Session());
}

extern "C" JNIEXPORT void JNICALL
Java_com_axiomzero_androidsuite_LocalModelRuntime_nativeCancel(JNIEnv *, jobject, jlong handle) {
    auto *session = reinterpret_cast<Session *>(handle);
    if (session != nullptr) {
        session->cancelled.store(true);
    }
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_axiomzero_androidsuite_LocalModelRuntime_nativeGenerate(
    JNIEnv *env, jobject, jlong handle, jstring prompt, jint max_tokens) {
    auto *session = reinterpret_cast<Session *>(handle);
    if (session == nullptr || session->model == nullptr || session->context == nullptr) {
        return error(env, "The local model is not loaded.");
    }
    if (max_tokens < 1 || max_tokens > 192) {
        return error(env, "Generation is limited to 192 tokens.");
    }

    const std::string input = to_string(env, prompt);
    if (input.empty() || input.size() > 6000) {
        return error(env, "The grounded prompt is empty or exceeds 6,000 bytes.");
    }
    session->cancelled.store(false);
    const llama_vocab *vocab = llama_model_get_vocab(session->model);
    llama_memory_clear(llama_get_memory(session->context), true);
    std::vector<llama_token> tokens(std::min<size_t>(input.size() + 8, 4096));
    const int32_t token_count = llama_tokenize(
        vocab, input.c_str(), static_cast<int32_t>(input.size()),
        tokens.data(), static_cast<int32_t>(tokens.size()), true, true);
    if (token_count < 0 || token_count > 4096 ||
        static_cast<uint64_t>(token_count) + static_cast<uint32_t>(max_tokens) > session->context_tokens) {
        return error(env, "The prompt and requested output exceed the bounded context length.");
    }
    tokens.resize(static_cast<size_t>(token_count));
    for (int32_t offset = 0; offset < token_count;) {
        if (session->cancelled.load()) {
            return error(env, "Generation cancelled.");
        }
        const int32_t batch_size = std::min<int32_t>(512, token_count - offset);
        if (llama_decode(session->context, llama_batch_get_one(tokens.data() + offset, batch_size)) != 0) {
            return error(env, "The local model could not evaluate the prompt.");
        }
        offset += batch_size;
    }

    llama_sampler *sampler = llama_sampler_chain_init(llama_sampler_chain_default_params());
    if (sampler == nullptr) {
        return error(env, "The local sampler could not be initialized.");
    }
    llama_sampler_chain_add(sampler, llama_sampler_init_greedy());
    std::string output;
    const llama_token eos = llama_vocab_eos(vocab);
    const llama_token eot = llama_vocab_eot(vocab);
    for (jint index = 0; index < max_tokens && !session->cancelled.load(); ++index) {
        const llama_token token = llama_sampler_sample(sampler, session->context, -1);
        if (token == eos || token == eot) {
            break;
        }
        char piece[256];
        const int32_t piece_size = llama_token_to_piece(vocab, token, piece, sizeof(piece), 0, false);
        if (piece_size > 0) {
            output.append(piece, static_cast<size_t>(
                std::min<int32_t>(piece_size, static_cast<int32_t>(sizeof(piece)))));
            if (output.size() > 8192) {
                break;
            }
        }
        llama_sampler_accept(sampler, token);
        if (index + 1 < max_tokens && llama_decode(session->context, llama_batch_get_one(&token, 1)) != 0) {
            break;
        }
    }
    llama_sampler_free(sampler);
    return new_string_from_utf8(
        env, session->cancelled.load() ? "Generation cancelled." : output);
}

extern "C" JNIEXPORT void JNICALL
Java_com_axiomzero_androidsuite_LocalModelRuntime_nativeFree(JNIEnv *, jobject, jlong handle) {
    delete reinterpret_cast<Session *>(handle);
}
