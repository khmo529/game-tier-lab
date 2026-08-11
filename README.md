# NoPickle Tierlist - NIKKE + BrownDust2 + Overwatch2 + Palworld 통합 관리 시스템

> WordPress 숏코드 기반 티어표 + GitHub Actions 자동화 + 이미지 보존형(v16) 업데이트 시스템

![WordPress](https://img.shields.io/badge/WordPress-6.x-21759B?logo=wordpress)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![GitHub Actions](https://img.shields.io/badge/Actions-Auto%20Deploy-2088FF?logo=githubactions)
![Status](https://img.shields.io/badge/Version-v16-success)

운영 사이트: [browndust2-tierlist](https://nopickle.co.kr/browndust2-tierlist/) | [nikke-tierlist](https://nopickle.co.kr/nikke-tierlist/) | [overwatch-tier](https://nopickle.co.kr/overwatch-tier/) | [palworld-tier](https://nopickle.co.kr/palworld-tier/)

---

## 📌 개요

NIKKE, BrownDust2, Overwatch2, Palworld 4개 게임의 티어리스트를 하나의 코드베이스에서 통합 관리하는 시스템입니다.

- **핵심 목표:** 외부 티어 소스를 크롤링하되, 로컬 이미지와 메타데이터는 절대 덮어쓰지 않는다
- **UI:** GeneratePress Child Theme + 바닐라 JS + SEO 최적화 + 광고 안정화
- **배포:** GitHub Actions 주간 자동 실행 → JSON 동기화 → SCP 자동 배포

### v16 핵심 원칙
> **이미지는 절대 안 건드린다. 등급(grade/tier)과 점수만 업데이트한다.**
> **외부 API DNS 차단 시 CDN으로 우회한다.**

```python
# ❌ 기존 로직 (버그) - 이미지까지 덮어씀 + wiki API 호출
CHAR_PATH.write_text(json.dumps(new_chars)) # 106B.png 404 + justia.png로 통일
requests.get("https://api.palworldgame.wiki/api/pals/123/icon") # ERR_NAME_NOT_RESOLVED 48개

# ✅ v16 로직 (안전) - 등급만 업데이트 + CDN 1순위
for c in chars:
    new_grade = name_to_grade.get(c['id'].upper())
    if new_grade:
        c['tier'] = new_grade  # tier만 바꿈, c['image']는 그대로!

# 이미지 로드 순서: charles8ff CDN (신팰 113,123) -> mlg404 CDN (012B.png) -> 로컬
```

---

## ✨ 주요 기능

- **등급 보존 업데이트 (v16):** `characters.json` / `pals.json` 기준, `grade/tier`, `score`, `work_level`만 갱신
- **이미지 안전화:** `assets/images/001.png, 012B.png` 체계, `api.palworldgame.wiki` 직접 호출 제거 → `ERR_NAME_NOT_RESOLVED` 해결
- **광고 안정화:** `.ad-box{width:100%; min-width:300px}` + `setTimeout push`로 `No slot size for availableWidth=0` 해결
- **자동 집계:** `weekly-update.json`을 파싱 결과가 아닌 실제 DB `Counter(c['tier'])`로 생성
- **고성능 UI:** `content-visibility: auto`, 필터/검색/정렬/모달, LiteSpeed Cache 대응

---

## 📁 폴더 구조 (4개 게임 통합)

```
games/
├── browndust2/
│   ├── data/
│   │   ├── characters.json       # 167명 DB (SS+~C, PVE/PVP/길드/악마성)
│   │   └── weekly-update.json    # Counter 집계: 전체 167개 / SS+:3 SS:3 S:7 A:8 B:146
│   └── tier_updater.py           # v15 - 등급만 업데이트, 이미지 보존
├── nikke/
│   ├── data/
│   │   ├── characters.json
│   │   └── weekly-update.json
│   └── tier_updater.py           # v15
├── overwatch2/
│   ├── data/
│   │   ├── characters.json
│   │   └── weekly-update.json
│   └── scripts/update_overwatch_weekly.py
└── palworld/
    ├── data/
    │   ├── pals.json             # 팰 전체 DB (S+~D, 001.png, 012B.png 대문자 B 규칙)
    │   ├── last_update.json      # 마지막 갱신 KST (404 방지용 필수 파일)
    │   └── weekly-update.json
    └── tier_updater.py           # v16 - wiki API 제거, 등급만 업데이트

wp-content/themes/generatepress-child/
├── browndust2-tier/
│   ├── data/                     # games/browndust2/data 와 동기화
│   ├── assets/images/            # 캐릭터 이미지 (slug.png, 215개+)
│   ├── functions-snippet.php     # bootstrap + SEO + 번역맵
│   ├── index.php
│   ├── style.css
│   └── script.js
├── nikke-tier/
├── overwatch-tier/
└── palworld-tier/
    ├── data/                     # games/palworld/data 와 동기화
    ├── assets/
    │   ├── images/               # 001.png, 012B.png (대문자 B) - 106B,111B,123,123B,113 포함
    │   ├── css/style.css         # v8 - ad-box width:100% fix
    │   └── js/tier.js            # v8 - CDN 1순위, wiki API 제거, ads setTimeout
    └── functions-snippet.php

.github/workflows/
├── tier-update.yml               # browndust2 + nikke (월요일 12시 KST)
├── overwatch2-tier.yml           # OW2 (월요일 11시 KST)
└── palworld-tier.yml             # Palworld (월요일 11시 KST) - SCP 배포
```

---

## 🚀 설치 방법

### 1. WordPress 테마 연동
`wp-content/themes/generatepress-child/functions.php`:

```php
require_once get_stylesheet_directory() . '/browndust2-tier/functions-snippet.php';
require_once get_stylesheet_directory() . '/nikke-tier/functions-snippet.php';
require_once get_stylesheet_directory() . '/overwatch-tier/functions-snippet.php';
require_once get_stylesheet_directory() . '/palworld-tier/functions-snippet.php';
```

### 2. 페이지 생성 및 숏코드

- `browndust2-tierlist`:
  ```
  [browndust2_tier title="브라운더스트2 티어 리스트"]
  ```
- `nikke-tierlist`:
  ```
  [nikke_tier title="니케 티어 리스트"]
  ```
- `overwatch-tier`:
  ```
  [overwatch_tier]
  ```
- `palworld-tier`:
  ```
  [palworld_tier]  # SEO + 광고 + last_update 포함 v8
  ```

> GeneratePress Child 활성화 후 LiteSpeed Cache > Purge All 필수

---

## 🤖 티어 자동 업데이트 (GitHub Actions)

### 동작 순서 (4개 게임 공통)
1. `games/{game}/data/characters.json` 로드
2. 외부 티어 크롤링 (Pocket Tactics, prydwen.gg, game8.co, palworld.gg)
3. 외부 등급 → `name_to_grade` 매핑 테이블
4. 기존 캐릭터는 `grade/tier` 필드만 업데이트 (`image`, `element`, `role` 유지)
5. 신캐는 `slug.png` 형식으로 추가 (CDN 자동 다운로드)
6. `weekly-update.json`은 실제 `Counter(c['grade'])`로 집계

### Palworld v16 특화
- **파일명 규칙:** `001.png`, `012B.png` (대문자 B) - 유저 캡처 리스트 기준
- **신팰 113, 123, 123B:** `mlg404`에는 없음, `charles8ff/palworld-assets` CDN에서 자동 로드
- **DNS 차단 대응:** `api.palworldgame.wiki` 호출 금지 → `cdn.jsdelivr.net`로 교체
- **광고 오류 대응:** `ad-box{width:100%; min-width:300px}` + `setTimeout push`

### 로컬 테스트
```bash
cd games/browndust2
python tier_updater.py

cd ../nikke
python tier_updater.py

cd ../palworld
python tier_updater.py  # v16 - 등급만 변경, 이미지 절대 안 건드림
```

### GitHub Actions 워크플로우 예시 (Palworld)
```yaml
name: Palworld Tier Update (Weekly) - v16 Image Safe
on:
  schedule:
    - cron: '0 2 * * 1' # 월요일 11:00 KST
  workflow_dispatch:
jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install requests
      - run: |
          python games/palworld/tier_updater.py
          mkdir -p wp-content/themes/generatepress-child/palworld-tier/data
          cp games/palworld/data/*.json wp-content/themes/generatepress-child/palworld-tier/data/
      - name: Commit & Push
        run: |
          git config user.name "NoPickle Bot"
          git config user.email "bot@nopickle.co.kr"
          git add -A
          if git diff --staged --quiet; then exit 0; fi
          git commit -m "auto: Palworld v16 $(date +%Y-W%V) - image safe, fix 404 & ads"
          git pull --rebase --autostash origin main
          git push origin main
      - name: Deploy to WP Server
        if: success()
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          port: ${{ secrets.SSH_PORT }}
          source: "wp-content/themes/generatepress-child/palworld-tier/data/*.json,wp-content/themes/generatepress-child/palworld-tier/assets/js/*.js,wp-content/themes/generatepress-child/palworld-tier/assets/css/*.css"
          target: "/var/www/nopickle.co.kr/wp-content/themes/generatepress-child/palworld-tier/"
          strip_components: 5
          overwrite: true
```

---

## 🖼 이미지 관리 규칙 (v16)

### 문제 원인 (스크린샷 기반)
- `106B.png, 111B.png, 096B.png, 123, 123B, 113` 404 → 로컬에 없는데 로컬부터 찾아서 404 10번씩 발생
- `last_update.json 404` → 파일이 GitHub에 없어서 fetch 실패
- `api.palworldgame.wiki 48개 ERR_NAME_NOT_RESOLVED` → 한국에서 DNS 차단
- `adsbygoogle.push() error: No slot size for availableWidth=0` → ad-box width 0

### 현재 규칙 (v16)
- **파일명 = ID:** `001.png`, `012B.png` (대문자 B), `granhildr-boo-ghost.png`
- **로드 순서 (palworld v8):** `charles8ff CDN (신팰 113,123) -> mlg404 CDN (001~111) -> 로컬 -> placeholder`
- **Wiki API 제거:** `https://api.palworldgame.wiki` 호출 금지, `cdn.jsdelivr.net` 사용
- **광고:** `.ad-box{width:100%; min-width:300px}` + JS에서 `setTimeout(push,1500)`로 width 0 해결
- **삭제 금지:** `justia.png` fallback 1개 유지, `zzz*` 파일 삭제 완료

```bash
# 없는 이미지 찾기
ls wp-content/themes/generatepress-child/palworld-tier/assets/images/ | grep -E "123|113"
# 없으면 CDN에서 자동 로드 (v8)

# 수동 다운로드 (선택)
curl -L https://cdn.jsdelivr.net/gh/charles8ff/palworld-assets@main/assets/images/paldeck/123.png -o 123.png
curl -L https://cdn.jsdelivr.net/gh/charles8ff/palworld-assets@main/assets/images/paldeck/123B.png -o 123B.png
curl -L https://cdn.jsdelivr.net/gh/charles8ff/palworld-assets@main/assets/images/paldeck/113.png -o 113.png
```

---

## 📝 JSON 스키마

### pals.json / characters.json
```json
{
  "id": "090B",
  "name": "Jormuntide Ignis",
  "ko": "조르문타이드 이그니스",
  "element": ["Fire","Dragon"],
  "tier": "S+",
  "type": "전투",
  "work": "점화4",
  "work_level": {"kindling":4},
  "max_work": 4,
  "desc": "화속 최강"
}
```

### weekly-update.json
```json
{
  "version": "2026년 08월 2주차 (W33)",
  "updated": "2026-08-11",
  "last_update_kst": "2026-08-11T11:00:00",
  "meta": "전체 37개 / S+:2 S:13 A:6 B:8 C:2",
  "total": 37,
  "grades": {"S+":2, "S":13, "A":6, "B":8, "C":2},
  "count": 37,
  "sources": ["mlg404/palworld-paldex-api (012B.png)", "charles8ff/palworld-assets (113,123 신팰)"]
}
```

---

## 🔧 functions-snippet.php 핵심 (v8)

### Palworld 광고 안정화
```php
// ad-box width 0 오류 방지
<div class="ad-box" style="width:100%;min-width:300px;min-height:120px">
  <ins class="adsbygoogle"
       style="display:block;width:100%;min-height:90px"
       data-ad-client="ca-pub-5335907721603724"
       data-ad-slot="4117852756"
       data-ad-format="auto"
       data-full-width-responsive="true"></ins>
</div>

// tier.js에서 setTimeout으로 push
setTimeout(() => {
  if(ad.parentElement.offsetWidth===0) return;
  (adsbygoogle = window.adsbygoogle || []).push({});
}, 1500);
```

### 번역맵 (따옴표 버그 수정 v4)
`Kardis' Bullet` 같은 작은따옴표 때문에 500 에러 → 큰따옴표 통일

---

## 🐛 자주 생기는 버그 & 해결 (v16 업데이트)

| 증상 | 원인 | 해결 |
| :--- | :--- | :--- |
| `last_update.json 404` | 파일이 GitHub에 없음 | `games/palworld/data/last_update.json` 생성 후 push, JS에서 `if(res.ok)` 체크 (v8) |
| `106B.png, 123, 113 404 x10` | 로컬에 없는데 로컬부터 탐색 | v8에서 CDN 1순위로 변경, `via.placeholder.com` 최종 fallback |
| `api.palworldgame.wiki ERR_NAME_NOT_RESOLVED 48개` | 한국 DNS 차단 | v16에서 해당 도메인 호출 완전 제거, jsDelivr CDN으로 교체 |
| `adsbygoogle.push() error: No slot size for availableWidth=0` | ad-box width 0에서 push | `.ad-box{width:100%; min-width:300px}` + `setTimeout 1.5s` push |
| SEO 글 사라짐 | functions.php에서 섹션 제거 | v8 functions-snippet.php에 SEO 테이블 복구 |
| 전체 167개 / S:0 | 파싱 실패 | `Counter(c['grade'])` 실제 집계 사용 |
| 전부 `justia.png`로 통일 | 이미지 URL 없는 파일 | CLEAN 버전 `characters_final_167_CLEAN.json`으로 복구 |
| Unknown Unknown 표시 | element, role Unknown | 정상 파일 복구, `bd2_t_ko()`로 한글 변환 |
| 페이지 500 오류 | `Kardis' Bullet` 작은따옴표 | v4 `functions-snippet.php` 사용 |

---

## 📌 최종 배포 체크리스트 (v16)

- [ ] `characters.json` / `pals.json` 등급 분포 정상인가? (SS+ 2개 이상, B 100개+)
- [ ] `assets/images/`에 `001.png, 012B.png` 규칙으로 100개+ 있는가?
- [ ] `123, 123B, 113` 신팰은 CDN에서 뜨는가? (로컬 없어도 OK - v8)
- [ ] `last_update.json`이 GitHub와 서버 양쪽에 있는가?
- [ ] `tier.js` v8 (CDN 1순위, wiki API 제거, ads setTimeout) 적용됐는가?
- [ ] `style.css` v8 (ad-box width:100%) 적용됐는가?
- [ ] `functions-snippet.php` v8 (SEO 복구) 적용됐는가?
- [ ] `tier_updater.py` v16 (이미지 보존) 적용됐는가?
- [ ] `weekly-update.json`의 `grades`가 실제 `Counter` 집계인가?
- [ ] LiteSpeed Cache > Purge All 했는가?
- [ ] 콘솔에 빨간 에러 0개인가? (ads, 404, ERR_NAME_NOT_RESOLVED)

---

## 👨💻 관리자 정보

- **사이트:** https://nopickle.co.kr
- **문의:** NoPickle (권혁민)
- **라이선스:** 이미지 저작권은 각 게임사(Shift Up, Neowiz, Blizzard, Pocketpair)에 있음, 티어 데이터는 자체 집계 및 2차 가공

> 이 저장소는 자동화 봇(NoPickle Bot)이 매주 월요일 11:00 KST에 업데이트합니다. 수동 실행은 Actions > Palworld Tier Update > Run workflow
