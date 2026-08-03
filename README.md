# NoPickle Tierlist - NIKKE + BrownDust2 통합 관리 시스템

> WordPress 숏코드 기반 티어표 + GitHub Actions 자동화 + 이미지 보존형(v15) 업데이트 시스템

![WordPress](https://img.shields.io/badge/WordPress-6.x-21759B?logo=wordpress)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![GitHub Actions](https://img.shields.io/badge/Actions-Auto%20Deploy-2088FF?logo=githubactions)
![Status](https://img.shields.io/badge/Version-v15-success)

운영 사이트: [https://nopickle.co.kr/browndust2-tierlist/](https://nopickle.co.kr/browndust2-tierlist/) | [https://nopickle.co.kr/nikke-tierlist/](https://nopickle.co.kr/nikke-tierlist/)

---

## 📌 개요

NIKKE(승리의 여신: 니케)와 BrownDust2(브라운더스트2) 두 게임의 티어리스트를 하나의 코드베이스에서 통합 관리하는 시스템입니다.

- **핵심 목표:** 외부 티어 소스(Pocket Tactics 등)를 크롤링하되, 로컬 이미지와 메타데이터는 절대 덮어쓰지 않는다
- **UI:** GeneratePress Child Theme + 바닐라 JS + SEO 최적화 템플릿
- **배포:** GitHub Actions 주간 자동 실행 → JSON 동기화 → 자동 커밋

### v15 핵심 원칙
> **이미지는 절대 안 건드린다. 등급(grade)과 점수만 업데이트한다.**

```python
# ❌ 기존 로직 (버그) - 이미지까지 덮어씀
CHAR_PATH.write_text(json.dumps(new_chars)) # 전부 justia.png로 통일

# ✅ v15 로직 (안전) - 등급만 업데이트
for c in chars:
    new_grade = name_to_grade.get(c['id'])
    if new_grade:
        c['grade'] = new_grade  # grade만 바꿈, c['image']는 그대로!
```

---

## ✨ 주요 기능

- **등급 보존 업데이트:** `characters.json` 167개 기준, `grade`, `pve/pvp/guild/boss/score`만 갱신
- **이미지 안전화:** `assets/images/slug.png` 체계, fallback 남용 방지
- **자동 집계:** `weekly-update.json`을 파싱 결과가 아닌 실제 DB `Counter(c['grade'])`로 생성
- **고성능 UI:** `content-visibility: auto`, 필터/검색/즐겨찾기/바텀시트, LiteSpeed Cache 대응
- **다국어/SEO:** `functions-snippet.php` 번역맵 + JSON-LD + OG 자동화

---

## 📁 폴더 구조

```
games/
├── nikke/
│   ├── data/
│   │   ├── characters.json       # 니케 전체 캐릭터 DB (등급, 스킬, 이미지 URL)
│   │   └── weekly-update.json    # 주간 메타 정보 (버전, 메타 요약, buff/nerf)
│   └── tier_updater.py           # v15 - 등급만 업데이트, 이미지는 보존
├── browndust2/
│   ├── data/
│   │   ├── characters.json       # 브더2 167명 DB (SS+~C, PVE/PVP/길드/악마성)
│   │   └── weekly-update.json    # 예: 전체 167개 / SS+:3 SS:3 S:7 A:8 B:146
│   └── tier_updater.py           # v15 - 이미지 절대 안 건드리는 안전한 버전
│
wp-content/themes/generatepress-child/
├── browndust2-tier/
│   ├── data/                     # games/browndust2/data 와 동기화 (배포 시 복사)
│   ├── assets/images/            # 캐릭터 이미지 (slug.png 형식, 215개+)
│   ├── functions-snippet.php     # bootstrap + SEO + 번역맵 (따옴표 버그 수정 v4)
│   ├── index.php                 # 티어표 UI 템플릿 v3
│   ├── style.css                 # High-End Refined UI v3 (content-visibility 최적화)
│   └── script.js                 # 필터, 검색, 즐겨찾기, 바텀시트
└── nikke-tier/                   # 니케 티어리스트 (구조 동일)
    ├── data/
    ├── assets/images/
    ├── functions-snippet.php
    ├── index.php
    ├── style.css
    └── script.js
```

---

## 🚀 설치 방법

### 1. WordPress 테마 연동
`wp-content/themes/generatepress-child/functions.php` 에 추가:

```php
// BrownDust2
require_once get_stylesheet_directory() . '/browndust2-tier/functions-snippet.php';
// NIKKE
require_once get_stylesheet_directory() . '/nikke-tier/functions-snippet.php';
```

### 2. 페이지 생성 및 숏코드 삽입

- `browndust2-tierlist` 페이지 생성:
  ```
  [browndust2_tier title="브라운더스트2 티어 리스트"]
  ```
- `nikke-tierlist` 페이지 생성:
  ```
  [nikke_tier title="니케 티어 리스트"]
  ```

> GeneratePress Child 테마 활성화 후 LiteSpeed Cache > Purge All 필수

---

## 🤖 티어 자동 업데이트 (GitHub Actions)

### 동작 순서
1. `games/browndust2/data/characters.json` 로드 (167개 기준)
2. 외부 티어 크롤링 (예: Pocket Tactics - https://www.pockettactics.com/brown-dust-2/tier-list)
3. 외부 등급 → `name_to_grade` 매핑 테이블로 변환
4. 기존 캐릭터는 `grade` 필드만 업데이트 (`image`, `element`, `role` 유지)
5. 신캐릭터가 있으면 `slug.png` 형식으로 추가 (Fandom 위키 자동 다운로드 시도)
6. `weekly-update.json`은 실제 캐릭터 등급으로 집계 (S:0 버그 방지)

### 로컬 테스트
```bash
cd games/browndust2
python tier_updater.py
# -> characters.json 등급만 변경, weekly-update.json 재생성

cd ../nikke
python tier_updater.py
```

### GitHub Actions 워크플로우 `.github/workflows/tier-update.yml`
```yaml
name: Tier Update (Weekly)
on:
  schedule:
    - cron: '0 3 * * 1' # 매주 월요일 12시 KST
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install requests beautifulsoup4
      - run: python games/browndust2/tier_updater.py
      - run: python games/nikke/tier_updater.py
      - name: Sync to wp theme
        run: |
          cp games/browndust2/data/*.json wp-content/themes/generatepress-child/browndust2-tier/data/
          cp games/nikke/data/*.json wp-content/themes/generatepress-child/nikke-tier/data/
      - name: Commit
        run: |
          git config user.name "tier-bot"
          git config user.email "bot@nopickle.co.kr"
          git add -A
          git commit -m "chore: weekly tier update $(date +%Y-%m-%d)" || exit 0
          git push
```

---

## 🖼 이미지 관리 규칙 (중요)

### 문제 원인
- 예전 파일명: `zzzzz-1762163612booghostgranhildr.png`, `justia.png` fallback 남용
- 새 파일명: `granhildr-boo-ghost.png` (slug 형식)

### 현재 규칙
- **파일명 = 캐릭터 ID:** `id = slugify(base + costume)`
  - 예: Granhildr + Boo Ghost → `granhildr-boo-ghost.png`
  - 예: Justia + Knight of Blood → `justia-knight-of-blood.png`
- **이미지 폴더:** `browndust2-tier/assets/images/` 및 `nikke-tier/assets/images/`
- **삭제 금지 파일:** `justia.png`는 fallback용으로 1개만 유지, 나머지 `zzz`로 시작하는 파일은 모두 삭제 완료
- **신규 업로드:** Fandom 위키에서 다운로드 후 `slug.png`로 저장. v14/v15가 자동 다운로드 시도, 실패 시 수동 업로드 필요

```bash
# 없는 이미지 찾기
python tier_updater.py
# [SKIP] Fandom에서 못 찾음, 수동 업로드 필요: granhildr-boo-ghost.png

# 수동 업로드 후 자동 인식
ls assets/images/ | grep granhildr
# granhildr-boo-ghost.png <- 정상 표시
```

---

## 📝 JSON 스키마

### characters.json
```json
{
  "id": "justia-knight-of-blood",
  "name": "저스티아 (피의 기사)",
  "name_en": "Justia",
  "base_en": "Justia",
  "base_ko": "저스티아",
  "costume": "Knight of Blood",
  "costume_ko": "피의 기사",
  "grade": "SS+",
  "element": "Fire",
  "role": "Tank",
  "type": "Limited",
  "pve": 9.5,
  "pvp": 9.0,
  "guild": 10.0,
  "boss": 8.5,
  "score": 9.25,
  "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/justia-knight-of-blood.png",
  "summary": "피 흡수로 버티는 탱커",
  "pros": ["생존 최상", "길드레이드 필수"],
  "cons": ["화속 약점"],
  "invest": 5,
  "beginner": true
}
```

### weekly-update.json
```json
{
  "version": "2026년 08월 2주차 (W31)",
  "updated": "2026-08-03",
  "meta": "전체 167개 / SS+:3 SS:3 S:7 A:8 B:146",
  "total": 167,
  "grades": { "SS+": 3, "SS": 3, "S": 7, "A": 8, "B": 146 },
  "buff": ["라텔", "유스티아"],
  "nerf": [],
  "note": "이번 주 길드레이드 상향으로 탱커 티어 조정"
}
```

---

## 🔧 functions-snippet.php 핵심

### 번역맵 (따옴표 버그 수정 v4)
`Kardis' Bullet` 같은 작은따옴표 때문에 500 에러가 나므로, v4부터는 큰따옴표로 통일.

```php
function bd2_translate_map() {
  return [
    "element" => [
      "Fire" => "화염", "Water" => "물", "Wind" => "바람",
      "Light" => "빛", "Dark" => "어둠"
    ],
    "role" => [
      "Tank" => "탱커", "Healer" => "힐러",
      "Support" => "서포터", "Physical DPS" => "물리 딜러"
    ],
    "costume" => [
      "Acolyte" => "수행사제",
      "Beach Vacation" => "해변 휴가",
      // ... 120개 매핑
    ]
  ];
}

function bd2_t_ko($en, $type) {
  $map = bd2_translate_map();
  return $map[$type][$en] ?? $en;
}
```

- 숏코드 등록: `add_shortcode('browndust2_tier', ...)`
- SEO: `wp_head`에 JSON-LD + `og:image` 자동 주입
- 템플릿 로드: `locate_template()` 대신 `get_stylesheet_directory() . '/browndust2-tier/index.php'` 직접 로드

---

## 📌 최종 배포 체크리스트

- [ ] `characters.json` 167개, 등급 분포 정상인가? (SS+ 3개 이상, B 100개+)
- [ ] `assets/images/`에 146개 이상 고유 이미지 있는가? `ls | wc -l`
- [ ] `zzz*` 파일 전부 삭제됐는가?
- [ ] `justia.png` fallback 1개만 존재하는가?
- [ ] `functions-snippet.php` v4 (작은따옴표 수정) 적용됐는가?
- [ ] `style.css` v3 (`content-visibility`) 적용됐는가?
- [ ] `tier_updater.py` v15 (이미지 보존) 적용됐는가?
- [ ] `weekly-update.json`의 `grades`가 실제 `Counter` 집계인가?
- [ ] LiteSpeed Cache > Purge All 했는가?
- [ ] https://nopickle.co.kr/browndust2-tierlist/ 에서 이미지 중복 없는가?

---

## 🐛 자주 생기는 버그 & 해결

| 증상 | 원인 | 해결 |
| :--- | :--- | :--- |
| 전체 167개 / S:0 A:0 B:0 | `fetch_tiers()` 파싱 실패 | v11+ 사용, `Counter(c['grade'])`로 실제 집계 |
| 전부 `justia.png`로 통일 | 이미지 URL이 존재하지 않는 파일 | CLEAN 버전 `characters_final_167_CLEAN.json`으로 복구 |
| Unknown Unknown 표시 | `element`, `role`이 Unknown | 정상 파일 복구, `functions-snippet.php`에서 `bd2_t_ko()`로 한글 변환 |
| 페이지 500 오류 | `Kardis' Bullet` 작은따옴표 파싱 에러 | v4 `functions-snippet.php` 사용 (큰따옴표로 수정) |
| 그란힐드르 (부끄고스트) 이미지 틀림 | `zzz` 파일 삭제됨, 매핑 누락 | `manual_clean` 매핑에 수동 추가 후 재매칭 |

---

## 👨‍💻 관리자 정보

- **사이트:** https://nopickle.co.kr
- **문의:** NoPickle (권혁민)
- **라이선스:** 이미지 저작권은 각 게임사(Shift Up, Neowiz)에 있음, 티어 데이터는 자체 집계 및 2차 가공

> 이 저장소는 자동화 봇(tier-bot)이 매주 월요일 03:00 UTC에 업데이트합니다. 수동 실행은 Actions > Tier Update > Run workflow
