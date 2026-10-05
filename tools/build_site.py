#!/usr/bin/env python3
"""Build self-contained static Pages HTML. Requires Markdown 3.11."""
from pathlib import Path
import html, json, shutil
import markdown

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
REPO='https://github.com/sftblw-pages/lg-g6-g600kr'
RELEASE=REPO+'/releases/tag/g600kr-2026-10-05'
SITE.mkdir(exist_ok=True)
(SITE/'.nojekyll').write_text('')
nav='<nav aria-label="주 메뉴"><a href="guide.html">설치 순서</a><a href="downloads.html">다운로드</a><a href="gapps.html">Google Play</a><a href="worklog.html">작업 기록</a><a href="kernel.html">커널 빌드</a></nav>'
def page(title,body,description):
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{html.escape(description,quote=True)}"><meta name="color-scheme" content="light"><title>{html.escape(title)} · G600KR Archive</title><link rel="stylesheet" href="style.css"></head>
<body><a class="screenreader" href="#main">본문으로 이동</a><header><a href="index.html">G600KR / ARCHIVE</a>{nav}</header><main id="main" class="shell">{body}</main><footer><div>실기 확인 2026-10-04–05 · 개인 실험 기록 · LG / LineageOS / TeamWin의 공식 배포가 아닙니다.<br>AI 작성·정리: OpenAI Codex · GPT-6 Astra (<code>gpt-6-astra</code>)<br><a href="{REPO}">GitHub 저장소</a> · <a href="notice.html">작성 정보·출처와 권리</a> · <a href="{RELEASE}">고정 릴리스</a></div></footer></body></html>'''

def write(name,title,body,description):
    (SITE/name).write_text(page(title,body,description),encoding='utf-8',newline='\n')

intro='''<section class="hero"><div class="eyebrow">A documented second life · LG G6</div><h1>서랍 속 G6에<br>Android 14를.</h1><p class="lead">G600KR 한 대에서 분해 없이 LineageOS를 부팅하고, 직접 빌드한 커널로 Wi-Fi 인터넷 연결과 Google Play 앱 설치까지 확인했습니다. 실제 사용한 파일과 설치 과정, 실패했던 지점까지 함께 남깁니다.</p><div class="actions"><a class="button" href="guide.html">설치 순서 읽기</a><a class="button secondary" href="downloads.html">파일과 검증값 받기</a></div></section>
<section class="facts" aria-label="확인한 결과"><div class="fact"><strong>G600KR</strong><span>KT · rev_11 실기 1대</span></div><div class="fact"><strong>Android 14</strong><span>LineageOS 21 비공식 빌드</span></div><div class="fact"><strong>Wi-Fi 연결</strong><span>AP 검색 · DNS · 인터넷 확인</span></div><div class="fact"><strong>분해 없음</strong><span>ENG 부트로더 우회 사용</span></div></section>
<div class="note"><strong>먼저 확인하세요.</strong> 정식 언락 키 방식이 아니며 잠금 표시는 남습니다. 데이터가 삭제되고, 부트로더 기록 실패 시 분해·EDL 복구가 필요할 수 있습니다. 다른 G6 변형 기종에는 그대로 적용하지 마세요.</div>
<section><h2>진행한 경로</h2><div class="cards"><article class="card"><span class="number">01 / PREPARE</span><h3>순정 기반 준비</h3><p>안티롤백 0 확인 → G600KR20p 설치 → Android 8에서 임시 루트와 본인 기기 백업.</p></article><article class="card"><span class="number">02 / INSTALL</span><h3>복구와 ROM 설치</h3><p>ENG LAF·aboot 기록 → TWRP 실행 → data 포맷 → LineageOS 21 첫 부팅.</p></article><article class="card"><span class="number">03 / REPAIR</span><h3>G600KR Wi-Fi 수정</h3><p>BCM4359 커널과 순정 Wi-Fi 파일 적용 → 실제 공유기와 인터넷 연결 확인.</p></article></div></section>
<section><h2>재현에 필요한 자료를 한곳에</h2><p>설명만 남겨 두지 않았습니다. KDZ, ROM, ENG, TWRP, 수정 boot와 드라이버를 Releases에 보관하고 파일마다 크기와 SHA-256을 제공합니다. KDZ 분할 파일을 합치는 도구와 커널의 전체 소스·설정·재포장 코드도 포함합니다.</p><p><a href="downloads.html">16개 배포 파일, 약 4.11GB 확인하기 →</a></p></section>
<section><h2>확인한 범위와 남은 부분</h2><p><span class="status">실기 확인</span> 부팅 · 초기 설정 · ADB · Wi-Fi 검색 · 공유기 연결 · DNS · 인터넷 · Google Play 실행과 앱 설치</p><p><span class="status">미검증</span> 통화 · 모바일 데이터 · 블루투스 · 카메라 · 장시간 안정성</p><p>같은 모델 한 대의 성공 기록입니다. 모든 기기의 성공이나 최신 보안 지원을 보장하지 않습니다. 공유용으로 일반화한 스크립트는 호스트 검사와 실제 실험 기록을 구분해 설명합니다.</p><p class="back"><a href="worklog.html">실패와 복구를 포함한 전체 작업 기록 →</a></p></section>
<section><h2>AI 작성 안내</h2><p>이 웹사이트의 설명과 작업 기록은 <strong>OpenAI Codex의 GPT-6 Astra (<code>gpt-6-astra</code>)</strong>가 실험 로그와 사용자 보고를 바탕으로 작성·정리했습니다. 기기 소유자 sftblw가 휴대폰의 물리적 조작과 화면 확인을 수행했습니다. 사용한 모델 식별자는 작업 세션 기록에서 확인했습니다.</p><p>LG 펌웨어, LineageOS, TWRP 등 기존 구성요소의 제작자와 출처는 <a href="notice.html">출처와 권리 안내</a>에 별도로 기록했습니다.</p></section>'''
write('index.html','LG G6에 Android 14',intro,'LG G6 G600KR의 ENG 우회, TWRP, LineageOS 21과 BCM4359 Wi-Fi 수정 기록 및 검증된 파일 보존 자료.')

for source,target,title in [('docs/GUIDE.md','guide.html','설치 순서'),('docs/WORKLOG.md','worklog.html','전체 작업 기록'),('docs/KERNEL.md','kernel.html','커널 재빌드'),('docs/GAPPS.md','gapps.html','Google Play 추가 설치'),('NOTICE.md','notice.html','출처와 권리')]:
    md=markdown.Markdown(extensions=['tables','fenced_code','toc'],extension_configs={'toc':{'toc_depth':'2-3','title':'이 문서의 순서'}})
    content=md.convert((ROOT/source).read_text(encoding='utf-8'))
    content=content.replace('href="docs/GUIDE.md"','href="guide.html"').replace('href="docs/WORKLOG.md"','href="worklog.html"').replace('href="GAPPS.md"','href="gapps.html"')
    body=f'<section class="hero"><div class="eyebrow">G600KR / {html.escape(title)}</div></section><div class="layout"><aside class="side">{nav}</aside><article class="article">{md.toc}{content}</article></div>'
    write(target,title,body,title+' — G600KR 한 대에서 확인한 절차와 근거입니다.')

manifest=json.loads((ROOT/'downloads/manifest.json').read_text(encoding='utf-8'))
rows=[]
for a in manifest['assets']:
    name=html.escape(a['name'])
    size=f"{a['size']/1000000:,.2f} MB"
    url=f"{REPO}/releases/download/{manifest['tag']}/{a['name']}"
    rows.append(f'<tr><td><a href="{url}">{name}</a><br><small>{html.escape(a["description"])}</small></td><td>{size}<br><small>{a["size"]:,} bytes</small></td><td><details><summary>SHA-256</summary><code class="hash">{a["sha256"]}</code></details></td></tr>')
body='''<section class="hero"><div class="eyebrow">DOWNLOADS / VERIFIED INPUTS</div><h1>설치에 사용한 파일과 검증값.</h1><p class="lead">외부 원문이 사라져도 설치 과정을 추적할 수 있도록 실제 입력 파일과 소스를 보관합니다. 내려받은 뒤 크기와 SHA-256을 확인하세요. 임시 루트 공개본은 비로드 디버그 경로만 익명화했으며 실행 코드·데이터는 원본과 같습니다.</p></section><div class="note">KDZ는 3개 조각을 모두 받아 도구로 합쳐야 합니다. 다른 사람의 기기 고유 백업은 포함하지 않습니다. 다운로드 전에 <a href="guide.html">대상 기종과 설치 조건</a>을 확인하세요.</div><h2>한 번에 받고 검증하기</h2><p>먼저 <a href="'''+REPO+'''/archive/refs/tags/g600kr-2026-10-05.zip">안내·도구 ZIP</a>을 풀고 그 폴더에서 Python 3.10 이상으로 실행합니다.</p><pre><code>python tools/release_files.py download --directory ../g6-files
python tools/release_files.py assemble --directory ../g6-files</code></pre><p>배포 파일 약 4.11GB와 합쳐진 KDZ 2.81GB가 저장됩니다. 휴대폰에는 아무것도 기록하지 않습니다.</p><p><a href="manifest.json">JSON 파일 목록</a> · <a href="SHA256SUMS">SHA256SUMS</a> · <a href="'''+RELEASE+'''">GitHub Releases에서 보기</a></p><h2>개별 다운로드</h2><table class="downloads"><thead><tr><th>파일 / 용도</th><th>크기</th><th>검증값</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table><h2>합쳐진 KDZ</h2><p><code>G600KR20P_00_1214.kdz</code> · 2,814,394,085바이트</p><pre><code>5218561668c0efa58907fc667d9d4e3dfaec012e7f22d2e2d72f7fce8e06e1af</code></pre><p>세 조각의 검증과 합쳐진 전체 파일 검증을 모두 통과해야 합니다. <a href="notice.html">파일의 출처와 권리 안내</a>도 함께 보관합니다.</p>'''
body += '<section><h2>선택: Google Play 추가 파일</h2><p>위 기본 16개 파일과 별도로 받는 패키지입니다. 실제 설치 후 Play 스토어 실행과 앱 다운로드를 확인했습니다. <a href="gapps.html">초기화 조건과 설치 절차</a>를 먼저 확인하세요.</p><p><a href="https://github.com/sftblw-pages/lg-g6-g600kr/releases/download/gapps-2026-10-05/MindTheGapps-14.0.0-arm64-20250203_200051.zip">MindTheGapps Android 14 ARM64 ZIP</a> · 431,524,182바이트 (431.52MB)</p><pre><code>6e1c3616862ce5b33e2b96074f86ae846eb1351a26a980e1ed140f8a7e7a4fd6</code></pre><p><a href="https://github.com/sftblw-pages/lg-g6-g600kr/releases/tag/gapps-2026-10-05">Google 앱 보존 릴리스</a> · <a href="gapps-manifest.json">파일 목록</a> · <a href="GAPPS-SHA256SUMS">ZIP 검증값</a> · <a href="gapps-installed-files.sha256">설치된 36개 파일 검증값</a></p></section>'
write('downloads.html','파일 다운로드',body,'실제 사용한 G600KR 펌웨어, LineageOS, TWRP, 커널과 SHA-256 다운로드 목록.')
for name in ('manifest.json','SHA256SUMS','gapps-manifest.json','GAPPS-SHA256SUMS','gapps-installed-files.sha256'):
    shutil.copyfile(ROOT/'downloads'/name,SITE/name)
print('Built 7 static HTML pages. No JavaScript or external assets required.')
