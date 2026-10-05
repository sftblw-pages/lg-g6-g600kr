# LG G6 G600KR → LineageOS 21

LGM-G600KR 한 대에서 **분해 없이 ENG 부트로더 우회 → TWRP → Android 14 → Wi-Fi 인터넷 연결 → Google Play 앱 설치**까지 확인한 기록과 재현 자료입니다. 실기 확인: 2026-10-04~05.

- [설치 안내 사이트](https://sftblw-pages.github.io/lg-g6-g600kr/)
- [파일 다운로드 / 고정 릴리스](https://github.com/sftblw-pages/lg-g6-g600kr/releases/tag/g600kr-2026-10-05)
- [설치 순서](docs/GUIDE.md) · [전체 작업 기록](docs/WORKLOG.md) · [커널 재빌드](docs/KERNEL.md)
- [파일 크기와 SHA-256](downloads/manifest.json) · [출처와 권리 안내](NOTICE.md)
- [Google Play 추가 설치](docs/GAPPS.md) · [선택 Google 앱 보존 릴리스](https://github.com/sftblw-pages/lg-g6-g600kr/releases/tag/gapps-2026-10-05)

## AI 작성 안내

이 웹사이트의 설명과 작업 기록은 **OpenAI Codex의 GPT-6 Astra (`gpt-6-astra`)**가 실험 로그와 사용자 보고를 바탕으로 작성·정리했습니다. 기기 소유자 sftblw가 휴대폰의 물리적 조작과 화면 확인을 수행했습니다. 모델 식별자는 작업 세션 기록에서 확인했습니다. 기존 펌웨어·ROM·복구 이미지 등 각 구성요소의 제작자와 출처는 [출처와 권리 안내](NOTICE.md)에 기록했습니다.

## 적용 범위

**LGM-G600KR / KT / rev_11**, 안티롤백 APPSBL·SBL1·TZ·RPM 모두 0인 실기에서 확인했습니다. 모든 G6의 설치를 보장하지 않습니다. ENG 방식은 정식 언락 키 방식과 다르며 `LOCK STATE locked`가 남습니다. 데이터가 삭제되고, 부트로더 기록 실패 시 분해·EDL 복구가 필요할 수 있습니다.

확인한 기능은 Android 14 부팅·초기 설정·ADB·Wi-Fi 검색·공유기 연결·DNS·인터넷 통신과 Google Play 실행·앱 설치입니다. 통화·모바일 데이터·블루투스·카메라·장시간 안정성은 미검증입니다. 2026-05-01 보안 패치를 표기하는 비공식 ROM이며 최신 보안 지원을 의미하지 않습니다.

## 파일 받기

저장소에는 안내·소스·스크립트·검증값을, Releases에는 실제 사용한 바이너리와 커널 소스 아카이브를 보관합니다. 외부 링크만 남겨 둔 배포가 아닙니다. 공개 저장소 ZIP을 풀거나 `git clone`으로 받은 뒤, Python 3.10 이상에서 실행합니다.

```text
python tools/release_files.py download --directory ../g6-files
python tools/release_files.py assemble --directory ../g6-files
```

첫 명령은 약 4.11GB를 다운로드하고 검증합니다. 두 번째는 3개 조각을 약 2.81GB KDZ로 합친 뒤 원본 SHA-256을 확인합니다. 기기에 연결하거나 기록하지 않습니다. 파일·백업·작업 공간을 합쳐 PC에 최소 20GB 이상 여유를 권장합니다. 커널을 직접 빌드할 때는 추가 공간이 필요합니다.

공개 임시 루트 바이너리만 비로드 디버그 정보의 PC 사용자 경로를 익명화했습니다. 실행되는 모든 PT_LOAD 바이트는 원본과 같습니다. [변경 검증 기록](downloads/su98-debug-anonymization.json)을 함께 제공합니다.

## 공개하지 않는 자료

다른 사람의 `modemst*`, `fsg`, `persist`, `factory`, DRM 등 기기 고유 백업을 자신의 폰에 쓰면 안 됩니다. 이 저장소에는 실기 시리얼, Wi-Fi 접속 정보, NV 백업, 사용자 데이터, 원시 진단 로그를 포함하지 않습니다. 도구가 만들어 주는 `private-backups`와 Wi-Fi 복구용 stage도 공개하지 마세요.

공유용으로 경로·기기 선택을 일반화한 도구는 원래 실험의 명령을 바탕으로 정리했습니다. 호스트에서 구문·해시·재포장·오류 중단을 검사했으며, 일반화한 모든 도구를 또 다른 기기에 실제 기록해 검증한 것은 아닙니다. 검사 실패를 무시하거나 보호 조건을 지워 진행하지 마세요.
