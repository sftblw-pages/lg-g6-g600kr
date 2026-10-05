# Wi-Fi 수정 커널과 재포장

## 정확한 입력

- 공개 소스: `rainbowdashh/android_kernel_lge_msm8996`, 커밋 `7e7397d497cdbfc0deedb9295d54d755f799fdd8`.
- Releases의 `kernel-source-7e7397d4.tar.gz`가 실제 빌드에 사용한 전체 아카이브입니다. 소스 파일은 수정하지 않고 설정을 변경했습니다.
- 원본 ROM 설정: `kernel/rom-original.config`.
- 사용한 입력 설정: `kernel/g600kr-wifi-only.config`.
- olddefconfig 이후 실제 확정 설정: `kernel/g600kr-wifi-resolved.config`.
- 변경은 BCMDHD_LEGACY / BCM43455 → BCMDHD_EXT / BCM4359 및 해당 종속 항목입니다. H870 모뎀 보정과 커널 명령행은 유지했습니다.
- Ubuntu의 Clang 14 + LLD 14, 병렬 작업 2개로 빌드했습니다. 이 오래된 트리는 임의의 최신 컴파일러와 호환된다고 보장하지 않습니다.

## Linux / WSL 빌드

호스트에 Clang/LLVM/LLD 14, make, GCC/G++, flex, bison, libssl 개발 파일, libelf 개발 파일, bc, Python 3를 준비합니다. Ubuntu에서는 `clang-14 llvm-14 lld-14 build-essential flex bison libssl-dev libelf-dev bc python3` 패키지에 해당합니다. 버전과 배포판에 따라 의존성 패키지 이름은 달라질 수 있습니다.

경로는 예시입니다. Linux 파일시스템에 소스와 출력을 두는 것이 좋습니다.

```sh
mkdir -p "$PWD/local/kernel-src"
tar -xzf ../g6-files/kernel-source-7e7397d4.tar.gz --strip-components=1 -C "$PWD/local/kernel-src"
export PATH="/usr/lib/llvm-14/bin:$PATH"
sh kernel/build.sh "$PWD/local/kernel-src" "$PWD/local/kernel-out"
python3 kernel/repack.py \
  --original ../g6-files/boot-lineage-original.img \
  --kernel local/kernel-out/arch/arm64/boot/Image.gz \
  --output local/boot-rebuilt.img
```

`local/kernel-out`에는 기존 `.config`가 없어야 합니다. 스크립트는 기존 설정을 덮어쓰지 않습니다. ARM64 vDSO 링크에 호스트 GNU ld가 선택되면 실패할 수 있어 `-fuse-ld=lld -Qunused-arguments`를 지정했습니다.

실제 실험에서 만든 `g600kr-wifi-Image.gz`도 Releases에 보존했습니다. 이것을 `--kernel`에 넣어 재포장하면 배포 중인 `boot-g600kr-wifi.img`와 동일한 SHA-256을 확인할 수 있습니다. 새로 컴파일한 커널은 빌드 시간·환경 등에 따라 바이너리 해시가 달라질 수 있습니다.

## 왜 Image.gz만 사용하는가

원래 ROM boot의 커널 gzip 뒤에는 DTB 5,793,035바이트가 붙어 있습니다. 재포장은 **커널 gzip만 교체하고 원래 DTB와 램디스크를 보존**합니다. 새 빌드의 Image.gz-dtb를 통째로 넣지 않습니다.

LG 호환 v0 boot의 ID는 kernel, ramdisk, 빈 second stage, 빈 별도 DT 필드의 크기를 모두 SHA-1에 반영합니다. 원본 이미지에서 공식을 먼저 검증합니다. 헤더의 kernel_size와 image_id 외 바이트가 바뀌지 않았는지도 검사합니다.

| 항목 | 검증값 |
| --- | --- |
| 최종 boot 크기 | 17,653,760바이트 |
| 최종 boot SHA-256 | `cbf044c07b499c4a3f94e587131e92d3c61b83946f2b6809e4477cd32f859eb5` |
| 보존 DTB SHA-256 | `974007cacf088b56f5b963997991dc58391994ee1f78a211272d1b1fb82fa7f0` |
| 보존 램디스크 SHA-256 | `5d68d45e78ff380eeb46f91b92223cc0bfb4cd8945f46153758fa73544809210` |

정확한 소스·설정·스크립트가 있어도 전체 LineageOS ROM의 비트 단위 재현을 보장하지 않습니다. ROM의 빌드 시점과 커널 소스 공개 시점은 달랐습니다. 최종 boot의 실기 확인 범위는 `kernel/tested-boot.json`과 전체 작업 기록에 남겼습니다.

## 임시 루트 소스

`src/g6-su98-local.c`와 업스트림 대비 `src/su98-local.patch`를 제공합니다. 실제 바이너리는 Zig 0.14.1의 aarch64-linux-musl 정적 빌드로 만들었습니다. 원작자 표기는 소스 헤더와 NOTICE에 보존했습니다. 커널 심볼 캐시를 끄고 readlink의 NUL 종료와 출력 처리를 보완했습니다.

```sh
zig cc -target aarch64-linux-musl -static -O2 src/g6-su98-local.c -o g6-su98-local
```

위는 재빌드 명령 형태이며, 도구 환경·링커 메타데이터 차이로 배포 바이너리와 같은 해시가 나온다는 보장은 없습니다. 배포 바이너리의 정확한 해시는 manifest에 있습니다. 이 취약점 시험은 소유·관리 권한이 있는 대상 기기에서만 수행합니다.
