# Google Play 추가 설치

2026-10-05, Wi-Fi 수정을 마친 이 G600KR에 **MindTheGapps를 추가하고 Play 스토어 실행·실제 앱 다운로드와 설치까지 확인**했습니다. ROM이나 수정 boot를 다시 기록하지 않았고, 기존 커널과 Wi-Fi 파일은 그대로 유지됐습니다.

대상은 앞에서 설치한 LineageOS 21 / Android 14 / ARM64와 H870 TWRP 3.5.2_10-0 조합입니다. Google 앱 없이도 LineageOS는 사용할 수 있습니다.

아래 명령은 [Google 앱 안내가 추가된 안내·도구 ZIP](https://github.com/sftblw-pages/lg-g6-g600kr/archive/refs/tags/gapps-2026-10-05.zip)을 풀거나 최신 저장소를 받은 폴더에서 실행합니다. 기존 기본 릴리스의 안내 ZIP에는 이 추가 문서와 설치 파일 해시 목록이 없습니다.

## 사용한 파일

- `MindTheGapps-14.0.0-arm64-20250203_200051.zip`
- 431,524,182바이트 (약 431.52MB)
- SHA-256: `6e1c3616862ce5b33e2b96074f86ae846eb1351a26a980e1ed140f8a7e7a4fd6`
- [이 기록의 보존 릴리스](https://github.com/sftblw-pages/lg-g6-g600kr/releases/tag/gapps-2026-10-05)
- [보존 ZIP 다운로드](https://github.com/sftblw-pages/lg-g6-g600kr/releases/download/gapps-2026-10-05/MindTheGapps-14.0.0-arm64-20250203_200051.zip)
- [MindTheGapps 공식 원본](https://github.com/MindTheGapps/14.0.0-arm64/releases/tag/MindTheGapps-14.0.0-arm64-20250203_200051)

기본 16개 파일을 받는 `tools/release_files.py`에는 이 선택 패키지가 포함되지 않습니다. 별도로 내려받아 검사합니다.

```powershell
Get-FileHash ../g6-files/MindTheGapps-14.0.0-arm64-20250203_200051.zip -Algorithm SHA256
```

## 이미 첫 부팅을 마친 경우

[LineageOS 공식 안내](https://github.com/LineageOS/lineage_wiki/blob/main/pages/gapps.md)는 Google 앱을 ROM 설치 직후, 첫 Android 부팅 전에 설치하도록 설명합니다. **이미 GApps 없이 부팅했다면 factory reset 후 설치해야 합니다.** 이 실험도 이미 초기 설정을 마친 상태여서 앱·설정 데이터를 초기화했습니다.

필요한 사용자 파일은 먼저 별도로 백업합니다. 아래 boot·system 백업은 사용자 데이터 백업이 아닙니다. Android에서 TWRP로 재부팅한 뒤 `adb devices`에서 **실제 G6의 recovery 시리얼**을 확인합니다. Android와 TWRP의 시리얼 접두부는 다를 수 있습니다.

```powershell
adb -s "현재 Android G6 시리얼" reboot recovery
adb devices -l
$G6 = "현재 TWRP G6 시리얼"
adb -s $G6 shell getprop ro.twrp.version
```

TWRP 3.5.2_10-0과 대상 기기를 확인합니다. System이 마운트돼 있으면 TWRP Mount 메뉴에서 해제한 뒤 현재 정상 상태를 PC에 백업합니다. 아래 도구는 크기와 기기·PC의 전체 SHA-256을 대조합니다. system은 약 5.86GB이므로 전송에 시간이 걸릴 수 있습니다.

```powershell
python tools/backup_partition.py --serial $G6 --partition boot --output ../private-backups/boot-before-gapps.img
python tools/backup_partition.py --serial $G6 --partition system --output ../private-backups/system-before-gapps.img
```

둘 다 `BACKUP_VERIFIED`인지 확인합니다. 본인 기기의 boot 백업 해시를 읽고, 실제 실험의 검사를 일반화한 읽기 전용 스크립트로 기기·ROM·커널·Wi-Fi 상태를 먼저 확인합니다.

```powershell
$G6BootHash = (Get-Content ../private-backups/boot-before-gapps.img.json -Raw | ConvertFrom-Json).sha256
adb -s $G6 push scripts/gapps-verify.sh /tmp/gapps-verify.sh
adb -s $G6 shell sh /tmp/gapps-verify.sh $G6 $G6BootHash --before
```

`GAPPS_DEVICE_PREFLIGHT_PASSED`가 나온 경우에만 ZIP을 전송합니다.

```powershell
adb -s $G6 push ../g6-files/MindTheGapps-14.0.0-arm64-20250203_200051.zip /tmp/g6-gapps.zip
adb -s $G6 shell sha256sum /tmp/g6-gapps.zip
adb -s $G6 shell twrp remountrw
```

기기의 ZIP 해시가 위 공식 값과 같아야 합니다. 이 실험은 system 여유 약 3.2GiB, `/tmp` 약 1.8GiB, 사용 가능한 RAM 약 3.4GiB에서 진행했습니다. 설치기는 ZIP을 RAM에 풀기 때문에 system 공간만 충분하다고 판단하지 않습니다.

**TWRP 화면 재구성이 끝난 뒤**, 다음 명령으로 앱·설정을 초기화합니다. 이 `wipe data`는 `/data/media`를 보존했고 cache도 포맷했습니다. 전체 내부 저장소를 지우는 `format data`와 구분합니다.

```powershell
adb -s $G6 shell twrp wipe data
```

초기화의 `Done`과 오류 없는 종료를 확인한 다음 설치합니다. 그 사이 Android로 부팅하지 않습니다.

```powershell
adb -s $G6 shell twrp install /tmp/g6-gapps.zip
adb -s $G6 pull /tmp/recovery.log ../private-backups/recovery-after-gapps.log
```

이 기기에서는 installer RC=0과 `Done!`을 확인했습니다. 설치기는 파일 복사 실패를 모두 종료 코드로 처리하지 않으므로 로그와 실제 파일을 함께 확인해야 합니다. 아래 해시 목록은 G6에 설치되는 36개 파일을 담고 있습니다. G6에서 제거되는 Pixel Tablet용 파일과 설치 중 생성되는 addon.d 스크립트는 목록에 포함하지 않습니다.

```powershell
adb -s $G6 push downloads/gapps-installed-files.sha256 /tmp/gapps-installed-files.sha256
adb -s $G6 shell sh /tmp/gapps-verify.sh $G6 $G6BootHash
```

36개 파일이 모두 `OK`이고 마지막에 `GAPPS_FILE_PERMISSIONS_VERIFIED`와 `GAPPS_FILES_BOOT_AND_WIFI_VERIFIED`가 나와야 합니다. 파일 소유권·권한·SELinux 표기, 생성된 addon.d 스크립트, 설치 전후 boot 전체 및 Wi-Fi 5개 파일의 동일성을 함께 검사합니다. 검사 실패 시 재부팅하지 말고 TWRP 상태에서 원인을 확인합니다. 기존 ROM 재설치는 Wi-Fi 수정까지 덮어쓸 수 있으므로 무작정 재설치하지 않습니다.

## 첫 부팅과 확인

```powershell
adb -s $G6 reboot
```

- 이 실기에서는 OS 변경 경고와 LG 로고를 거쳐 초기 설정으로 진행했습니다. 경고 자체가 성공을 보장하지 않으며, 반복되거나 전원이 꺼지면 실제 부팅 상태를 확인해야 합니다.
- Wi-Fi와 Google 계정 설정은 휴대폰에서 직접 진행합니다. 초기 설정의 ‘휴대전화 준비 중’에 시간이 걸릴 수 있습니다.
- **‘Lineage 복구 모드를 OS와 함께 업데이트’는 체크 해제하여 TWRP를 유지합니다.**
- 필요한 경우 USB 디버깅을 다시 허용합니다. 이번 사후 확인에는 루트 디버깅이 필요하지 않았습니다.
- Play 스토어 실행과 자동 업데이트를 PC에서 확인했고, 소유자가 실제 앱 다운로드·설치 성공을 확인했습니다. Wi-Fi 인터넷도 다시 검증했습니다.

Google Play 설치가 모든 앱의 기기 인증·DRM·무결성 검사를 통과한다는 뜻은 아닙니다. 이 실험에서는 Google 음성 서비스의 초기 부팅 오류 한 건이 관찰됐으며 음성 합성 기능은 따로 검증하지 않았습니다. 한국어 입력기는 이 ROM에 기본 제공되지 않았고 추가 키보드 앱은 설치하지 않았습니다.
