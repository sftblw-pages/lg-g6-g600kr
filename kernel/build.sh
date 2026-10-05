#!/bin/sh
# Run in Linux/WSL. Uses the exact input configuration, not another model defconfig.
set -eu
src=${1:?Usage: build.sh SOURCE_DIRECTORY OUTPUT_DIRECTORY}
out=${2:?Usage: build.sh SOURCE_DIRECTORY OUTPUT_DIRECTORY}
task=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
src=$(CDPATH= cd -- "$src" && pwd)
mkdir -p "$out"
out=$(CDPATH= cd -- "$out" && pwd)
test "$src" != "$out"
test -f "$src/drivers/net/wireless/bcmdhd_ext/Kconfig"
if [ -e "$out/.config" ]; then
    echo 'Refusing an existing .config; use a new output directory.' >&2
    exit 1
fi
cp "$task/g600kr-wifi-only.config" "$out/.config"
build_make() {
    make -C "$src" O="$out" ARCH=arm64 \
        CC="clang-14 -fuse-ld=lld -Qunused-arguments" HOSTCC=gcc HOSTCXX=g++ \
        LD=ld.lld-14 AR=llvm-ar-14 NM=llvm-nm-14 OBJCOPY=llvm-objcopy-14 \
        OBJDUMP=llvm-objdump-14 STRIP=llvm-strip-14 LLVM_IAS=1 \
        CROSS_COMPILE=aarch64-linux-gnu- CROSS_COMPILE_ARM32=arm-linux-gnueabi- "$@"
}
build_make olddefconfig
build_make -j"${JOBS:-2}" Image.gz-dtb
sha256sum "$out/arch/arm64/boot/Image.gz"
echo 'Use Image.gz with repack.py; keep the original ROM DTBs.'
