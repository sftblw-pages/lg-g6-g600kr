# G600KR 설치 순서

이 안내는 **LGM-G600KR 한 대에서 성공한 순서**를 공개용으로 정리한 것입니다. 기기 조건 확인·개별 백업·쓰기 후 검증을 포함합니다. 처음부터 끝까지 읽고 필요한 파일을 모두 받은 다음 시작하세요. 한 명령이라도 오류를 반환하면 다음 쓰기나 재부팅으로 넘어가지 않습니다.

## 0. 대상과 준비물

- 물리 모델 **LGM-G600KR / KT / rev_11**. H870으로 표시되는 TWRP나 ROM 속성만으로 물리 기종을 판단하지 않습니다.
- 시작 상태는 G600KR30c / Android 9였습니다. 안티롤백은 APPSBL(LK)·SBL1·TZ·RPM 모두 **0**임을 기본 전화 앱 `*#546368#*600#` → SVC Menu → Version Info에서 직접 확인했습니다. 값이 다르면 이 안내를 적용하지 않습니다.
- 휴대폰의 모든 사용자 데이터가 삭제됩니다. 배터리는 60% 이상, 안정적인 USB 케이블과 PC 전원을 준비합니다. 부트로더 기록 실패는 분해 후 EDL 복구를 요구할 수 있습니다.
- Windows, 최신 Android SDK Platform Tools의 `adb`·`fastboot`, Python 3.10 이상이 필요합니다. [Platform Tools 공식 다운로드](https://developer.android.com/tools/releases/platform-tools).
- 공개 저장소를 PC에 내려받아 그 폴더에서 명령을 실행합니다. 아래 명령은 PowerShell 기준이며 `adb`, `fastboot`, `python`이 PATH에 있어야 합니다. 바이너리는 `../g6-files`, 본인 백업은 `../private-backups`에 둡니다.

```powershell
python tools/release_files.py download --directory ../g6-files
python tools/release_files.py assemble --directory ../g6-files
```

다운로드 도구는 파일 크기와 SHA-256을 검사합니다. 수동으로 받은 경우 `python tools/release_files.py verify --directory ../g6-files`로 검사할 수 있습니다. KDZ 세 조각은 압축 파일이 아닌 순서대로 분할한 원본 바이트입니다. `assemble`로 합친 파일만 LGUP에 지정합니다.

연결 오류로 중단되면 같은 명령을 다시 실행합니다. 이미 완료한 파일은 검증 후 재사용합니다. PC나 앱의 비정상 종료로 임시 파일이 남았다는 오류가 나오면 같은 명령 끝에 `--restart`를 붙이면 됩니다. 이 옵션은 해당 작업의 `.downloading` 또는 `.assembling` 임시 파일만 버리고 재시도하며, 완성된 파일은 덮어쓰지 않습니다.

## 1. 순정 Android 8로 내리기

1. `LGMobileDriver_WHQL_Ver_4.8.0.exe`의 LG 서명을 확인하고 설치합니다.
2. `LGUP-Cmd-1.15.0.6-Common-2.1.0.23.zip`을 풉니다. LGUP_Cmd.exe와 LGUP_Common.dll을 함께 둡니다.
3. 휴대폰 전원을 완전히 끄고 USB를 뺍니다. **볼륨 올림만 누른 채 PC USB 연결** → Firmware Update 화면에서 버튼을 놓습니다.
4. Windows 장치 관리자에서 LG 다운로드 포트의 COM 번호를 확인합니다. 아래의 `com3`은 예시입니다.
5. CMD에서 다음 형태로 실행합니다. DLL과 KDZ 경로의 따옴표를 반드시 유지합니다.

```text
LGUP_Cmd.exe com3 "C:\G6\LGUP_Common.dll" "C:\G6\G600KR20P_00_1214.kdz"
```

이 CLI의 기본 REFURBISH가 실행되며 userdata를 초기화합니다. 실제 실험은 100% / Download Complete / 종료 코드 0을 확인했습니다. 초기 콘솔의 COM0 표시가 실제 COM 포트와 다를 수 있어 DLL 로그의 Port Open과 모델·파일을 함께 봐야 합니다. 기록 중 케이블을 빼지 마세요.

첫 부팅은 오래 걸릴 수 있습니다. 초기 설정을 완료하고 USB 디버깅과 PC 허용을 다시 설정합니다. Google 계정 로그인은 설치 자체의 필수 조건이 아닙니다. 기존 계정의 기기 보호가 요구되는 경우에는 본인 계정으로 해결해야 합니다.

```powershell
adb devices
$G6 = "현재 adb devices에 나온 시리얼"
adb -s $G6 shell getprop ro.lge.swversion
adb -s $G6 shell getprop ro.build.version.release
adb -s $G6 shell uname -a
```

**G600KR20p / Android 8.0.0 / 3.18.71-perf+**를 확인합니다. ADB 연결이 안 되면 잠금 해제·USB 디버깅 승인·케이블을 확인합니다. 이 실험의 Android 9에서는 USB 구성을 MIDI로 바꾸는 것이 도움이 됐습니다.

## 2. 임시 루트와 본인 기기 백업

사용한 바이너리는 CVE-2019-2215 기반이며 커널 메모리를 변경합니다. Android 9에서는 실패했고 위 Android 8에서 성공했습니다. 실패 시 멈추거나 재부팅될 수 있습니다. 무한 반복 실행하지 않습니다.

공개 `g6-su98-local`은 원본의 **로드되지 않는 DWARF 디버그 정보에서 PC 사용자 경로만 같은 길이로 익명화**했습니다. ELF의 모든 PT_LOAD 구간은 바이트 단위로 동일합니다. 실행 코드·데이터는 변경하지 않았으며 공개본 해시는 다운로드 목록에 있습니다. 원본과 공개본의 차이는 `downloads/su98-debug-anonymization.json`과 `tools/make_public_su98.py`로 확인할 수 있습니다.

```powershell
adb -s $G6 push ../g6-files/g6-su98-local /data/local/tmp/g6-su98-local
adb -s $G6 shell chmod 700 /data/local/tmp/g6-su98-local
adb -s $G6 shell '/data/local/tmp/g6-su98-local "id; getenforce; setenforce 1; getenforce"'
```

`uid=0`, `Permissive`, `Enforcing`을 확인합니다. 일반 ADB 셸은 계속 uid=2000일 수 있습니다. 임시 루트 명령마다 마지막에 SELinux Enforcing을 복원합니다.

```powershell
adb -s $G6 push scripts/backup-stock.sh /data/local/tmp/backup-stock.sh
adb -s $G6 shell '/data/local/tmp/g6-su98-local "sh /data/local/tmp/backup-stock.sh"'
New-Item -ItemType Directory -Force ../private-backups
adb -s $G6 pull /data/local/tmp/g6-stock-20p-backup ../private-backups/stock20p
python tools/verify_stock.py ../private-backups/stock20p
```

`BACKUP_COMPLETE`와 `ALL_58_PRIVATE_BACKUPS_VERIFIED`가 모두 필요합니다. 51개 파티션과 7개 기본 GPT의 약 522MB 백업이며 Android 8로 내린 뒤의 상태입니다. 아직 system·userdata·cache는 포함하지 않습니다. 이 백업에는 기기 고유 설정이 있으므로 **본인 PC에만 보관**합니다. 기존 백업 경로가 있으면 스크립트가 중단합니다. 내용을 검사하지 않고 지우거나 덮어쓰지 마세요.

## 3. ENG LAF와 aboot 기록

이 단계는 부팅 검증 동작을 영구적으로 바꿉니다. 정식 부트로더 unlock 명령이 아닙니다. 스크립트는 정확한 펌웨어·파티션 크기·현재 순정 해시·입력 해시·백업을 확인하고, **LAF 먼저 → aboot 마지막**으로 기록합니다. 오류 시 복구를 시도하지만 전원 단절까지 복구를 보장하지 않습니다.

```powershell
adb -s $G6 shell mkdir -p /data/local/tmp/g6-eng-stage
adb -s $G6 push ../g6-files/aboot.img /data/local/tmp/g6-eng-stage/aboot.img
adb -s $G6 push ../g6-files/laf.img /data/local/tmp/g6-eng-stage/laf.img
adb -s $G6 push scripts/apply-eng.sh /data/local/tmp/apply-eng.sh
adb -s $G6 shell '/data/local/tmp/g6-su98-local "sh /data/local/tmp/apply-eng.sh"'
```

성공 출력은 `LAF_WRITE_READBACK_VERIFIED`, `ABOOT_WRITE_READBACK_VERIFIED`, `ENG_APPLY_COMPLETE_NO_REBOOT`, `Enforcing`입니다. 모두 확인한 뒤:

```powershell
adb -s $G6 reboot bootloader
fastboot devices
```

Fastboot 화면의 `secure yes`, `unlocked no`, `LOCK STATE locked`는 이 방식에서 실제로 남았습니다. 이를 없애려고 임의의 unlock 명령을 추가하지 않습니다.

## 4. Fastboot 드라이버와 TWRP

Fastboot에 장치가 안 나오고 Windows에 VID_18D1 / PID_D00D의 드라이버 오류가 있으면 `g6-fastboot-google-catalog.cab`을 풉니다. 장치 하드웨어 ID가 정확히 일치할 때만 관리자 터미널에서 해당 INF를 설치합니다.

```powershell
New-Item -ItemType Directory -Force ../g6-fastboot-driver
expand.exe -F:* ../g6-files/g6-fastboot-google-catalog.cab ../g6-fastboot-driver
pnputil /add-driver ../g6-fastboot-driver/android_winusb.inf /install
```

실제 사용한 것은 Google 11.0.0.0 / Microsoft 서명 패키지입니다. INF 수정이나 Windows 서명 검사 해제는 필요하지 않았습니다.

`fastboot devices`의 현재 시리얼을 사용합니다. ENG 이후 시리얼의 모델 접두부가 바뀔 수 있습니다.

```powershell
$FastbootG6 = "현재 fastboot devices에 나온 시리얼"
fastboot -s $FastbootG6 flash recovery ../g6-files/twrp-3.5.2_10-0-h870.img
fastboot -s $FastbootG6 reboot recovery
```

이 실험에서는 임시 `fastboot boot`가 서명 검사로 거부됐고, `fastboot reboot recovery`는 일반 Android로 부팅됐습니다. 순정 Android가 recovery 앞부분을 순정으로 복구했습니다. 같은 현상이라면 현재 ADB 시리얼을 다시 확인하고 다음 검증된 경로를 사용합니다.

```powershell
adb devices
$G6 = "현재 Android ADB 시리얼"
adb -s $G6 push ../g6-files/twrp-3.5.2_10-0-h870.img /data/local/tmp/twrp-3.5.2_10-0-h870.img
adb -s $G6 push scripts/reapply-twrp.sh /data/local/tmp/reapply-twrp.sh
adb -s $G6 shell '/data/local/tmp/g6-su98-local "sh /data/local/tmp/reapply-twrp.sh"'
```

이 스크립트는 ENG 적용 후의 G600LR20p 표기, flash_recovery 정지, 검증된 recovery 상태만 허용합니다. `TWRP_REAPPLY_READBACK_VERIFIED`와 `Enforcing`을 확인한 뒤 `adb -s $G6 reboot recovery`를 실행합니다. 검사에 실패하면 해시 조건을 지워 강행하지 않습니다.

TWRP 로고·메뉴와 `adb devices`의 recovery 상태를 확인합니다. 암호가 맞는데 복호화가 실패하는 경우가 있었습니다. 이때 Cancel → Keep Read Only로 진입했습니다. `/data`를 포맷하기 전까지는 PIN 복호화 오류와 실제 PIN 불일치를 구분하세요.

## 5. 순정 system 백업, data 포맷, LineageOS 설치

TWRP의 현재 ADB 시리얼을 `$G6`에 넣습니다. 먼저 순정 system 약 5.86GB를 PC에 백업합니다. System이 쓰기 가능으로 마운트됐다면 TWRP Mount 메뉴에서 해제하고 실행합니다.

```powershell
python tools/backup_partition.py --serial $G6 --partition system --output ../private-backups/system-before-lineage.img
```

`BACKUP_VERIFIED`를 확인한 뒤 모든 사용자 데이터를 삭제하는 다음 명령을 실행합니다.

```powershell
adb -s $G6 shell twrp format data
adb -s $G6 reboot recovery
```

재부팅 후 TWRP가 완전히 뜰 때까지 기다립니다. `adb -s $G6 shell mount`에서 `/data`가 ext4로 정상 마운트됐는지 확인합니다. `/tmp` 파일은 재부팅으로 사라지므로 ROM을 다시 전송합니다.

```powershell
adb -s $G6 push ../g6-files/lineage-21.0-20260531-UNOFFICIAL-h870-BLMOD.zip /tmp/g6-lineage21.zip
adb -s $G6 push scripts/lineage-preflight.sh /tmp/g6-install-preflight.sh
adb -s $G6 shell sh /tmp/g6-install-preflight.sh
adb -s $G6 shell twrp remountrw
```

`LINEAGE_INSTALL_PREFLIGHT_PASSED`가 필요합니다. remountrw 뒤 TWRP 화면 재구성이 끝날 때까지 기다립니다. 즉시 install을 이어 보내면 FIFO 대기가 걸린 사례가 있습니다. 메뉴가 안정된 다음:

```powershell
adb -s $G6 shell twrp install /tmp/g6-lineage21.zip
adb -s $G6 shell 'dd if=/dev/block/bootdevice/by-name/boot bs=4096 count=4290 2>/dev/null | sha256sum'
```

설치 로그에서 `script succeeded: result was [1.000000]`, boot 읽기 해시에서 **`0db389f0d9223d6b4aa4e0a60e3c2c2bbc0b1bfb29e1d773ef4bd2aea47cd05f`**를 확인합니다. 실패하면 재부팅하지 말고 TWRP 상태에서 원인을 확인합니다.

```powershell
adb -s $G6 reboot
```

세 점이 도는 LineageOS 애니메이션 다음 초기 설정 화면이 나왔습니다. 이 단계에서는 Wi-Fi가 동작하지 않았으므로 연결을 건너뛰고 설정했습니다. USB 디버깅을 다시 허용한 뒤 `adb shell getprop sys.boot_completed`가 `1`인지 확인합니다. 모델명이 H870으로 표시돼도 물리 기종이 바뀐 것은 아닙니다.

## 6. G600KR Wi-Fi 수정 적용

기본 H870 ROM은 BCM43455 드라이버를 사용해 이 기기의 BCM4359 계열 칩을 인식하지 못했습니다. 공개 파일의 수정 boot와 순정 Wi-Fi 파일 **5개를 함께** 적용해야 합니다.

LineageOS에서 `adb reboot recovery`로 TWRP에 들어갑니다. OS가 변경됐다는 LG 경고가 잠시 보일 수 있습니다. 실제로 TWRP가 실행되고 recovery ADB가 연결되는지 확인합니다. TWRP의 현재 시리얼을 `$G6`에 다시 설정합니다.

먼저 아래 도구로 **이 기기의 현재 boot·Wi-Fi 파일을 새로 읽어** PC 복구본과 전송용 stage를 만듭니다. 이 명령은 파티션을 기록하거나 재부팅하지 않습니다.

```powershell
python tools/prepare_wifi.py --serial $G6 --assets ../g6-files --out ../private-backups/wifi-stage
```

`PRIVATE_BACKUP_AND_STAGE_READY`가 필요합니다. stage에는 본인 시리얼과 전체 boot 백업이 들어 있으므로 공유하지 않습니다. ROM 버전·원본 boot 앞부분·TWRP·ENG 해시가 다르면 중단합니다. 재실행에는 기존 결과를 덮어쓰지 않는 새 경로를 사용합니다.

```powershell
adb -s $G6 shell mkdir -p /tmp/g6-wifi
adb -s $G6 push ../private-backups/wifi-stage/. /tmp/g6-wifi/
adb -s $G6 shell sh /tmp/g6-wifi/apply.sh --check-only
```

`WIFI_FIX_PREFLIGHT_PASSED`와 `READ_ONLY_PREFLIGHT_COMPLETE`를 확인한 후에만 실제 기록합니다.

```powershell
adb -s $G6 shell sh /tmp/g6-wifi/apply.sh
```

`STOCK_G600_WIFI_FILES_READBACK_VERIFIED`와 `WIFI_KERNEL_READBACK_VERIFIED_NO_REBOOT`를 모두 확인하면 `adb -s $G6 reboot`로 부팅합니다. 새 커널과 Wi-Fi 적용을 함께 검증합니다.

실패 시 TWRP를 유지하고 원인을 확인합니다. 다시 들어온 TWRP에서는 `/tmp`가 사라졌으므로 **PC에 남긴 같은 기기의 stage**를 재전송한 뒤 다음으로 원래 LineageOS boot·Wi-Fi 파일을 복원할 수 있습니다.

```powershell
adb -s $G6 shell mkdir -p /tmp/g6-wifi
adb -s $G6 push ../private-backups/wifi-stage/. /tmp/g6-wifi/
adb -s $G6 shell sh /tmp/g6-wifi/restore.sh
```

`KNOWN_BOOTABLE_LINEAGE_RESTORED_AND_VERIFIED_NO_REBOOT` 확인 후 재부팅합니다. 이 복원은 수정 전 LineageOS로 돌아가는 것이며 순정 LG OS 전체 복원이 아닙니다.

## 7. 실제 동작 확인

- 설정 화면에 Wi-Fi 목록이 보이고 자신의 공유기에 연결되는지 확인합니다. 비밀번호는 휴대폰에 직접 입력합니다.
- Android 14, LineageOS 21.0-20260531-UNOFFICIAL-h870, 부팅 완료 상태를 확인합니다.
- 브라우저의 실제 웹 페이지 접속으로 DNS와 인터넷 통신을 확인합니다. 이 실험에서는 IP·도메인 ping 성공과 Android의 VALIDATED 상태도 확인했습니다.
- root 디버깅을 진단용으로 켰다면 작업 후 `adb unroot`를 실행하고 개발자 옵션도 필요에 맞게 정리합니다.
- 통화·모바일 데이터·블루투스·카메라·장시간 안정성은 이 공개 기록에서 검증하지 않았습니다.

## 복구에 관하여

원본 백업과 KDZ는 실패 가능성을 줄이는 자료이지 복구 성공 보증이 아닙니다. ENG 쓰기 실패로 Fastboot·TWRP·다운로드 모드가 모두 없어지면 본 안내의 소프트웨어 복구만으로 해결되지 않을 수 있습니다. 그런 상황에서 임의의 다른 모델 부트로더나 타인의 NV 백업을 쓰지 마세요. 본 실험에서는 후면 분해·테스트포인트·EDL을 사용하지 않았으며 그 복구 절차를 검증하지 않았습니다.
