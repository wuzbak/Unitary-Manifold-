cmake_minimum_required(VERSION 3.22.1)

project("sdam" VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ── Vendored ggwave v0.4.2 (MIT licence) ─────────────────────────────────────
set(GGWAVE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/ggwave)

add_library(ggwave STATIC
    ${GGWAVE_DIR}/src/ggwave.cpp
)

target_include_directories(ggwave PUBLIC
    ${GGWAVE_DIR}/include
    ${GGWAVE_DIR}/src        # fft.h and reed-solomon/ headers live here
)

# ── SDAM JNI shared library ───────────────────────────────────────────────────
add_library(sdam SHARED sdam_jni.cpp)

target_include_directories(sdam PRIVATE
    ${GGWAVE_DIR}/include
)

target_compile_options(sdam PRIVATE
    -O3
    -ffast-math
    -Wall
    -Wextra
)

# Android system libraries
find_library(log-lib log)

target_link_libraries(sdam
    ggwave          # vendored static ggwave lib
    ${log-lib}      # __android_log_print
    android         # ANativeActivity etc.
    OpenSLES        # low-latency audio — present on all API 26+ devices
)
