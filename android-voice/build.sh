#!/bin/sh
# Builds libobscurantvoice.so for 64-bit ARM phones from whisper.cpp 1.9.5.
# usage: build.sh <whisper.cpp source> <android ndk> <output dir>
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
FLAGS="-ffile-prefix-map=$HOME=/build"
cmake -S "$HERE" -B "$HERE/build" -DWHISPER_SRC="$1" -DCMAKE_TOOLCHAIN_FILE="$2/build/cmake/android.toolchain.cmake" \
  -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-26 -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS="$FLAGS" -DCMAKE_CXX_FLAGS="$FLAGS" > "$HERE/cmake.log"
cmake --build "$HERE/build" -j 12 --target obscurantvoice > "$HERE/make.log" 2>&1 || { tail -20 "$HERE/make.log"; exit 1; }
mkdir -p "$3"
"$2"/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-strip --strip-unneeded -o "$3/libobscurantvoice.so" "$HERE/build/libobscurantvoice.so"
