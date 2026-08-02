# NIKKE 티어표 (GeneratePress Child Theme)

토스/카카오페이 감성의 프리미엄 UI로 만든 "승리의 여신: 니케" 전체 캐릭터 티어표 페이지입니다.

## 설치 방법 (2가지 방식 모두 지원)

### 1) 페이지 템플릿 방식
1. GeneratePress Child Theme 폴더에 `nikke-tier/` 를 통째로 복사합니다.
   경로 예: `wp-content/themes/generatepress_child/nikke-tier/`
2. `nikke-tier/index.php` 를 `page-nikke-tier.php` 로 복사해 테마 루트에 두면 
   워드프레스에서 "Nikke Tier" 템플릿을 선택할 수 있습니다.
3. functions.php 에 아래 스니펫을 추가합니다.

```php
require_once get_stylesheet_directory() . '/nikke-tier/functions-snippet.php';
```

### 2) 숏코드 방식 (Gutenberg 호환)
페이지/글 어디에서든:

```
[nikke_tier]
```

## 데이터 업데이트

- `data/characters.json` : 전체 캐릭터 목록
- `data/weekly-update.json` : 주간 변경사항, 메타 정보

JSON만 수정하면 UI가 전부 반영됩니다.

## 파일 구조

```
nikke-tier/
├─ index.php                 # 페이지 템플릿 (GP 호환)
├─ functions-snippet.php     # 숏코드 + 에셋 등록
├─ style.css                 # 토스풍 디자인 시스템
├─ script.js                 # 컴포넌트화된 로직
├─ data/
│  ├─ characters.json
│  └─ weekly-update.json
└─ assets/
   └─ images
```

## 특징
- 토스/카카오페이/Apple/Hoyolab 감성 미니멀 UI
- 모바일 퍼스트, Sticky Filter, Bottom Sheet, FAB
- 다크모드, 즐겨찾기(LocalStorage), 공유/URL 복사
- SEO: JSON-LD (Breadcrumb, FAQ), OG/Twitter 태그 자동 삽입
- Lazy Load (IntersectionObserver), WebP 지원, 코드 컴포넌트화
- Adsense 슬롯 3곳 (첫 티어 끝 / 중간 / 하단)
