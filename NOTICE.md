# 출처와 권리

## AI 작성 정보

이 웹사이트의 설명과 작업 기록은 **OpenAI Codex의 GPT-6 Astra (`gpt-6-astra`)**가 실험 로그와 사용자 보고를 바탕으로 작성·정리했습니다. 모델 식별자는 작업 세션 기록에서 확인했습니다. 기기 소유자 sftblw가 휴대폰의 물리적 조작과 화면 확인을 수행했습니다.

AI 작성 표기는 이 사이트의 설명과 기록에 관한 것입니다. 아래 LG 펌웨어, LineageOS, TWRP 및 다른 기존 구성요소의 제작자와 권리는 각 원저작자에게 있습니다.

## 구성요소별 출처와 권리

이 프로젝트는 LG, LineageOS, TeamWin의 공식 배포가 아닙니다. 기존 파일의 출처와 권리 표기를 유지하며, 제3자 파일에 새로운 라이선스를 부여하지 않습니다. 공개되어 있다는 이유만으로 모든 구성요소가 자유 재배포 라이선스라고 주장하지 않습니다. 각 구성요소의 기존 라이선스·이용 조건이 적용됩니다.

| 구성요소 | 출처 / 비고 |
| --- | --- |
| G600KR20p KDZ | [AndroidFileHost 원본 패키지](https://androidfilehost.com/?fid=17825722713688290866), [독립 MD5 대조](https://lg-firmwares.com/downloads-file/17445/G600KR20P_00_1214). 원본 Credits와 링크 파일은 `notices/kdz/`에 보존. LG 순정 펌웨어 |
| ENG aboot / LAF | 소유자가 [XDA ENG 우회 안내](https://xdaforums.com/t/guide-lg-g6-bootloader-unlock-2025.4772845/)에서 확보해 제공한 `eng.zip`. 실제 사용한 두 파일만 배포. 동봉된 CRC 오류의 중첩 ZIP은 제외. LG/Qualcomm 구성요소 |
| LineageOS 21 BLMOD | [Rainbow_Dash의 ENG 대응 설명](https://xdaforums.com/t/guide-lg-g6-bootloader-unlock-2025.4772845/page-5#post-90611082), [배포 폴더](https://drive.google.com/drive/folders/1eNkIKYt29yycOa2nr7mqRuYIAFLBb692). 여러 라이선스와 제조사 바이너리를 포함하는 비공식 빌드. 업스트림 파일을 수정하지 않고 보존 |
| TWRP 3.5.2_10-0 H870 | 위 XDA 안내에서 연결한 LG 보존 배포본. TeamWin 및 해당 기기 유지보수자 작업 |
| 수정 커널 | [rainbowdashh/android_kernel_lge_msm8996](https://github.com/rainbowdashh/android_kernel_lge_msm8996/tree/7e7397d497cdbfc0deedb9295d54d755f799fdd8), 커밋 고정. 커널 전체 소스 아카이브와 사용한 설정·빌드·재포장 스크립트 제공. Linux COPYING은 `notices/Linux-COPYING`, 개별 소스의 라이선스 표기도 유지 |
| Wi-Fi 파일 | G600KR20p 순정 system에서 추출한 5개 펌웨어/설정 파일. 기기 고유 NV 파티션 백업이 아님. LG/Broadcom 구성요소 |
| su98 임시 루트 | [Karma2424 보존 저장소](https://github.com/Karma2424/cve2019-2215-3.18), Alexander R. Pruss의 3.18 수정, Google Project Zero의 Jann Horn·Maddie Stone 및 Grant Hernandez의 원작. 헤더 크레딧·원문 README·수정 소스·차이 패치 보존 |
| LGUP CLI | [실제 참조한 배포 원문](https://plzking4me.tistory.com/117). LG 서명 Cmd 1.15.0.6 + Common 2.1.0.23, 원 패키지 ReadMe 포함 |
| LG USB 드라이버 | LGMobileDriver WHQL 4.8.0, LG 서명 실행 파일 |
| Fastboot 드라이버 | [Microsoft Update 카탈로그](https://www.catalog.update.microsoft.com/Search.aspx?q=VID_18D1%26PID_D00D), 항목 76f2c233-6100-4a64-8bee-113c2da0991d. Google 11.0.0.0 / Microsoft 서명 CAB 원본 |

서명·해시는 파일의 동일성 및 서명자 확인 자료이며, 특정 기기의 안전성이나 재배포 허가 자체를 증명하지 않습니다. 제3자 배포물은 해당 권리자의 저작물입니다. 권리·출처 정정이 필요하면 저장소 Issues로 알려 주세요.

공개용 su98 실행 파일에는 디버그 정보의 PC 사용자 경로를 익명화한 변경만 있습니다. 실행 코드·데이터를 포함한 모든 ELF PT_LOAD 구간은 실기에서 사용한 원본과 동일합니다. 원본은 작업 기록의 SHA-256, 공개본은 manifest의 SHA-256으로 구분하며 익명화 도구와 위치별 검증 보고서를 제공합니다. 제조사 펌웨어·ROM·TWRP·수정 boot·드라이버에는 이 변경을 적용하지 않았습니다.

`kernel-source-7e7397d4.tar.gz`는 수정 커널 빌드에 사용한 전체 공개 소스입니다. `kernel/`의 입력·확정 설정, `kernel/build.sh`, `kernel/repack.py`, 원본 ROM boot와 실제 빌드의 Image.gz를 함께 제공하여 커널 교체 과정을 추적할 수 있게 했습니다. 전체 LineageOS ROM을 처음부터 완전 재빌드하거나 비트 단위로 재현했다는 의미는 아닙니다.
