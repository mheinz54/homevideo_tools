FFmpeg 64-bit static Windows build from www.gyan.dev

Version: 4.3.1-2021-01-01-essentials_build-www.gyan.dev

License: GPL v3

Source Code: https://github.com/FFmpeg/FFmpeg/commit/89daac5fe2

release-essentials build configuration: 

    --enable-gpl
    --enable-version3
    --enable-static
    --disable-w32threads
    --disable-autodetect
    --enable-fontconfig
    --enable-iconv
    --enable-gnutls
    --enable-libxml2
    --enable-gmp
    --enable-lzma
    --enable-zlib
    --enable-libsrt
    --enable-libssh
    --enable-libzmq
    --enable-avisynth
    --enable-sdl2
    --enable-libwebp
    --enable-libx264
    --enable-libx265
    --enable-libxvid
    --enable-libaom
    --enable-libopenjpeg
    --enable-libvpx
    --enable-libass
    --enable-libfreetype
    --enable-libfribidi
    --enable-libvidstab
    --enable-libvmaf
    --enable-libzimg
    --enable-amf
    --enable-cuda-llvm
    --enable-cuvid
    --enable-ffnvcodec
    --enable-nvdec
    --enable-nvenc
    --enable-d3d11va
    --enable-dxva2
    --enable-libmfx
    --enable-libgme
    --enable-libopenmpt
    --enable-libopencore-amrwb
    --enable-libmp3lame
    --enable-libtheora
    --enable-libvo-amrwbenc
    --enable-libgsm
    --enable-libopencore-amrnb
    --enable-libopus
    --enable-libspeex
    --enable-libvorbis
    --enable-librubberband

For macOS, place executable FFmpeg and FFprobe binaries in one of these folders:

    macos/arm64/ffmpeg       macos/arm64/ffprobe
    macos/x86_64/ffmpeg      macos/x86_64/ffprobe
    macos/universal/ffmpeg   macos/universal/ffprobe

The app prefers a matching bundled binary, then checks standard Homebrew locations,
then falls back to a command found on PATH.
The binaries must include libass for subtitle rendering and libx264, yadif, and
xfade support for the app's video operations. Include the applicable FFmpeg
license and source/build information with any distributed binaries.

