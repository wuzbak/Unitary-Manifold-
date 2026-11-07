cmake_minimum_required(VERSION 3.22.1)
project(axiomzero_llama_jni LANGUAGES C CXX)

include(FetchContent)
set(LLAMA_CPP_REVISION "9f0e5098a5d5d8adb8dd5c59036ae2a38ab07db9" CACHE STRING "" FORCE)
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(LLAMA_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(LLAMA_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(LLAMA_BUILD_SERVER OFF CACHE BOOL "" FORCE)
set(LLAMA_BUILD_COMMON OFF CACHE BOOL "" FORCE)
set(GGML_NATIVE OFF CACHE BOOL "" FORCE)
set(GGML_OPENMP OFF CACHE BOOL "" FORCE)
set(GGML_LLAMAFILE OFF CACHE BOOL "" FORCE)
set(GGML_VULKAN OFF CACHE BOOL "" FORCE)
set(GGML_BACKEND_DL OFF CACHE BOOL "" FORCE)

FetchContent_Declare(
    llama_cpp
    GIT_REPOSITORY https://github.com/ggml-org/llama.cpp.git
    GIT_TAG ${LLAMA_CPP_REVISION}
    GIT_SHALLOW FALSE
    GIT_PROGRESS TRUE
)
FetchContent_MakeAvailable(llama_cpp)

execute_process(
    COMMAND git -C "${llama_cpp_SOURCE_DIR}" rev-parse HEAD
    OUTPUT_VARIABLE LLAMA_CPP_CHECKED_OUT_REVISION
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE LLAMA_CPP_GIT_RESULT
)
if(NOT LLAMA_CPP_GIT_RESULT EQUAL 0 OR NOT LLAMA_CPP_CHECKED_OUT_REVISION STREQUAL LLAMA_CPP_REVISION)
    message(FATAL_ERROR "llama.cpp source revision did not match the pinned commit")
endif()

add_library(axiomzero_llama SHARED llama_jni.cpp)
target_compile_features(axiomzero_llama PRIVATE cxx_std_17)
target_compile_options(axiomzero_llama PRIVATE -Wall -Wextra -Werror)
target_link_libraries(axiomzero_llama PRIVATE llama android log)
