import json, os, requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

DATA_DIR = "games/nikke/data"
CHAR_FILE = os.path.join(DATA_DIR, "characters.json")
WEEKLY_FILE = os.path.join(DATA_DIR, "weekly-update.json")
RAW_FILE = os.path.join(DATA_DIR, "prydwen_raw.json")

EN_TO_KO = {
    "Scarlet": "홍련",
    "Scarlet: Black Shadow": "스칼렛",
    "Dorothy": "도로시",
    "Crown": "크라운",
    "Liter": "리터",
    "Red Hood": "레드후드",
    "Modernia": "모더니아",
    "Blanc": "블랑",
    "Noir": "누아르",
    "Noah": "노아",
    "Rapi": "라피",
    "Rapi: Red Hood": "라피 RH",
    "Volume": "볼륨",
    "Centi": "센티",
    "Mary": "메리",
    "Anis": "아니스",
    "Neon": "네온",
    "Ludmilla": "루드밀라",
    "Privaty": "프리바티",
    "Laplace": "라플라스",
}
KO_TO_EN = {v:k for k,v in EN_TO_KO.items()}
TIER_ORDER = {"SSS":0,"SS":1,"S":2,"A":3,"B":4,"C":5}
PRYDWEN_MAP = {"SSS":"SSS","SS":"SS","S":"S","A":"A","B":"B","C":"C","D":"C","F":"C"}

FALLBACK_JSON = """[
  {
    "id": 12,
    "name": "홍련",
    "tier": "SSS",
    "rarity": "SSR",
    "company": "필그림",
    "weapon": "AR",
    "element": "화염",
    "burst": "III",
    "position": "화력형",
    "content": [
      "스토리",
      "레이드",
      "PVP",
      "유니온"
    ],
    "rating": 5,
    "scores": {
      "story": 5,
      "boss": 5,
      "pvp": 5,
      "raid": 5,
      "union": 5
    },
    "pros": [
      "압도적 광역 화력",
      "자버프 100% 유지 쉬움",
      "보스전 최상위 딜러"
    ],
    "cons": [
      "초기 세팅 무거움",
      "저코어 성능 낮음"
    ],
    "overload": [
      "ELE ↑",
      "공격력 ↑",
      "치명타 피해 ↑"
    ],
    "cube": "재장전 큐브",
    "team": [
      "홍련 · 크라운 · 리터",
      "도로시(비추천)"
    ],
    "priority": [
      "3스킬 → 2스킬 → 1스킬"
    ],
    "reroll": true,
    "history": [
      "SS",
      "SS",
      "S",
      "SS",
      "SS",
      "SS",
      "SS",
      "SSS"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Scarlet.jpg"
  },
  {
    "id": 15,
    "name": "도로시",
    "tier": "SS",
    "rarity": "SSR",
    "company": "필그림",
    "weapon": "SR",
    "element": "전기",
    "burst": "II",
    "position": "지원형",
    "content": [
      "레이드",
      "보스",
      "유니온"
    ],
    "rating": 5,
    "scores": {
      "story": 4,
      "boss": 5,
      "pvp": 3,
      "raid": 5,
      "union": 5
    },
    "pros": [
      "강력한 코드 파훼",
      "보스전 안정성",
      "고유 버프 유틸"
    ],
    "cons": [
      "PVP 미비",
      "숙련도 요구"
    ],
    "overload": [
      "장탄수 ↑",
      "치명타 확률 ↑",
      "공격력 ↑"
    ],
    "cube": "탄창 큐브",
    "team": [
      "도로시 · 크라운 · 홍련"
    ],
    "priority": [
      "1스킬 → 3스킬 → 2스킬"
    ],
    "reroll": false,
    "history": [
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SS"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Dorothy.jpg"
  },
  {
    "id": 1,
    "name": "크라운",
    "tier": "SSS",
    "rarity": "SSR",
    "company": "핀윙",
    "weapon": "MG",
    "element": "철갑탄",
    "burst": "II",
    "position": "지원형",
    "content": [
      "스토리",
      "레이드",
      "PVP",
      "유니온"
    ],
    "rating": 5,
    "scores": {
      "story": 5,
      "boss": 5,
      "pvp": 5,
      "raid": 5,
      "union": 5
    },
    "pros": [
      "최상위 서포터",
      "전 컨텐츠 필수",
      "자버프 유지 쉬움"
    ],
    "cons": [
      "기재값 세팅 필요"
    ],
    "overload": [
      "공격력 ↑",
      "치명타 피해 ↑",
      "ELE ↑"
    ],
    "cube": "장탄수 큐브",
    "team": [
      "필수 · 조합 무관"
    ],
    "priority": [
      "3스킬 → 2스킬 → 1스킬"
    ],
    "reroll": true,
    "history": [
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Crown.jpg"
  },
  {
    "id": 2,
    "name": "리터",
    "tier": "SSS",
    "rarity": "SSR",
    "company": "테트라라인",
    "weapon": "MG",
    "element": "미사일",
    "burst": "III",
    "position": "화력형",
    "content": [
      "스토리",
      "보스",
      "레이드",
      "유니온"
    ],
    "rating": 5,
    "scores": {
      "story": 5,
      "boss": 5,
      "pvp": 3,
      "raid": 5,
      "union": 5
    },
    "pros": [
      "폭발 광역 딜",
      "레이드 최적",
      "코어 파괴 우수"
    ],
    "cons": [
      "PVP 활용 낮음"
    ],
    "overload": [
      "공격력 ↑",
      "치명타 피해 ↑",
      "ELE ↑"
    ],
    "cube": "장탄수 큐브",
    "team": [
      "리터 · 크라운 · 홍련"
    ],
    "priority": [
      "3스킬 → 2스킬"
    ],
    "reroll": true,
    "history": [
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Liter.jpg"
  },
  {
    "id": 7,
    "name": "레드후드",
    "tier": "SS",
    "rarity": "SSR",
    "company": "필그림",
    "weapon": "AR",
    "element": "철갑탄",
    "burst": "I·II·III",
    "position": "화력형",
    "content": [
      "스토리",
      "보스",
      "PVP"
    ],
    "rating": 5,
    "scores": {
      "story": 5,
      "boss": 4,
      "pvp": 5,
      "raid": 4,
      "union": 4
    },
    "pros": [
      "버스트 단계 유연성",
      "1인 3역",
      "고코어 시 성능 폭발"
    ],
    "cons": [
      "코어 의존도 큼"
    ],
    "overload": [
      "ELE ↑",
      "치명타 피해 ↑",
      "공격력 ↑"
    ],
    "cube": "재장전 큐브",
    "team": [
      "레드후드 · 크라운 · 리터"
    ],
    "priority": [
      "3스킬 → 1스킬 → 2스킬"
    ],
    "reroll": true,
    "history": [
      "S",
      "S",
      "S",
      "SS",
      "S",
      "S",
      "S",
      "SS"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Red Hood B1.jpg"
  },
  {
    "id": 4,
    "name": "모더니아",
    "tier": "S",
    "rarity": "SSR",
    "company": "미샤라",
    "weapon": "AR",
    "element": "화염",
    "burst": "III",
    "position": "화력형",
    "content": [
      "스토리",
      "레이드",
      "유니온"
    ],
    "rating": 4,
    "scores": {
      "story": 4,
      "boss": 4,
      "pvp": 3,
      "raid": 4,
      "union": 4
    },
    "pros": [
      "안정적 지속 딜",
      "무료 배포로 진입 좋음"
    ],
    "cons": [
      "최신 딜러에 밀림"
    ],
    "overload": [
      "ELE ↑",
      "치명타 확률 ↑"
    ],
    "cube": "재장전 큐브",
    "team": [
      "모더니아 · 크라운 · 노아"
    ],
    "priority": [
      "3스킬 → 2스킬"
    ],
    "reroll": false,
    "history": [
      "SS",
      "SS",
      "SS",
      "SS",
      "SS",
      "SS",
      "SS",
      "S"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Modernia.jpg"
  },
  {
    "id": 5,
    "name": "스칼렛",
    "tier": "SS",
    "rarity": "SSR",
    "company": "미샤라",
    "weapon": "AR",
    "element": "화염",
    "burst": "III",
    "position": "화력형",
    "content": [
      "스토리",
      "레이드",
      "PVP"
    ],
    "rating": 5,
    "scores": {
      "story": 5,
      "boss": 4,
      "pvp": 4,
      "raid": 4,
      "union": 4
    },
    "pros": [
      "광역 처리 우수",
      "자체 생존기"
    ],
    "cons": [
      "최상위 보스전 부족"
    ],
    "overload": [
      "공격력 ↑",
      "치명타 피해 ↑"
    ],
    "cube": "재장전 큐브",
    "team": [
      "스칼렛 · 크라운 · 리터"
    ],
    "priority": [
      "3스킬 → 2스킬"
    ],
    "reroll": true,
    "history": [
      "SS",
      "SS",
      "SS",
      "SS",
      "SS",
      "SS",
      "SS",
      "SS"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Scarlet.jpg"
  },
  {
    "id": 6,
    "name": "블랑",
    "tier": "SSS",
    "rarity": "SSR",
    "company": "필그림",
    "weapon": "AR",
    "element": "수속성",
    "burst": "I",
    "position": "탱커형",
    "content": [
      "스토리",
      "보스",
      "레이드",
      "유니온"
    ],
    "rating": 5,
    "scores": {
      "story": 5,
      "boss": 5,
      "pvp": 4,
      "raid": 5,
      "union": 5
    },
    "pros": [
      "최상위 탱커",
      "팀 무적 부여",
      "전 컨텐츠 필수"
    ],
    "cons": [
      "딜 기여 낮음"
    ],
    "overload": [
      "체력 ↑",
      "공격력 ↑",
      "방어력 ↑"
    ],
    "cube": "체력 큐브",
    "team": [
      "블랑 · 누아르 · 딜러"
    ],
    "priority": [
      "1스킬 → 3스킬"
    ],
    "reroll": true,
    "history": [
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS",
      "SSS"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Blanc.jpg"
  },
  {
    "id": 8,
    "name": "누아르",
    "tier": "SS",
    "rarity": "SSR",
    "company": "필그림",
    "weapon": "SG",
    "element": "화염",
    "burst": "II",
    "position": "지원형",
    "content": [
      "스토리",
      "보스",
      "레이드"
    ],
    "rating": 5,
    "scores": {
      "story": 5,
      "boss": 5,
      "pvp": 3,
      "raid": 5,
      "union": 4
    },
    "pros": [
      "블랑 시너지",
      "안정적 힐"
    ],
    "cons": [
      "단독 활용 애매"
    ],
    "overload": [
      "공격력 ↑",
      "치명타 피해 ↑"
    ],
    "cube": "탄창 큐브",
    "team": [
      "누아르 · 블랑 · 딜러"
    ],
    "priority": [
      "1스킬 → 2스킬"
    ],
    "reroll": true,
    "history": [
      "SS",
      "SS",
      "SS",
      "SS",
      "SS",
      "SS",
      "SS",
      "SS"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Noir.jpg"
  },
  {
    "id": 9,
    "name": "노아",
    "tier": "S",
    "rarity": "SSR",
    "company": "필그림",
    "weapon": "RL",
    "element": "수속성",
    "burst": "I",
    "position": "탱커형",
    "content": [
      "스토리",
      "유니온"
    ],
    "rating": 4,
    "scores": {
      "story": 4,
      "boss": 3,
      "pvp": 5,
      "raid": 3,
      "union": 4
    },
    "pros": [
      "PVP 상위권",
      "무적 유틸"
    ],
    "cons": [
      "보스전 낮음"
    ],
    "overload": [
      "체력 ↑",
      "방어력 ↑"
    ],
    "cube": "체력 큐브",
    "team": [
      "노아 · 태버사"
    ],
    "priority": [
      "1스킬 → 3스킬"
    ],
    "reroll": false,
    "history": [
      "S",
      "S",
      "S",
      "S",
      "S",
      "S",
      "S",
      "S"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Noah.jpg"
  },
  {
    "id": 10,
    "name": "라피",
    "tier": "A",
    "rarity": "SSR",
    "company": "카운터즈",
    "weapon": "AR",
    "element": "화염",
    "burst": "III",
    "position": "화력형",
    "content": [
      "스토리"
    ],
    "rating": 3,
    "scores": {
      "story": 3,
      "boss": 3,
      "pvp": 3,
      "raid": 2,
      "union": 3
    },
    "pros": [
      "범용 딜러",
      "초반 유용"
    ],
    "cons": [
      "엔드컨텐츠 부족"
    ],
    "overload": [
      "공격력 ↑"
    ],
    "cube": "재장전 큐브",
    "team": [
      "라피 · 아니스 · 네온"
    ],
    "priority": [
      "3스킬"
    ],
    "reroll": false,
    "history": [
      "A",
      "A",
      "A",
      "A",
      "A",
      "A",
      "A",
      "A"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Rapi.jpg"
  },
  {
    "id": 21,
    "name": "라피 RH",
    "tier": "S",
    "rarity": "SSR",
    "company": "카운터즈",
    "weapon": "SR",
    "element": "화염",
    "burst": "III",
    "position": "화력형",
    "content": [
      "보스",
      "레이드"
    ],
    "rating": 4,
    "scores": {
      "story": 3,
      "boss": 5,
      "pvp": 3,
      "raid": 4,
      "union": 4
    },
    "pros": [
      "보스전 신규 강자",
      "조준 딜 우수"
    ],
    "cons": [
      "광역 부족"
    ],
    "overload": [
      "공격력 ↑",
      "치명타 피해 ↑"
    ],
    "cube": "탄창 큐브",
    "team": [
      "라피RH · 크라운 · 태버사"
    ],
    "priority": [
      "3스킬 → 2스킬"
    ],
    "reroll": true,
    "history": [
      "-",
      "-",
      "-",
      "-",
      "-",
      "-",
      "-",
      "S"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Rapi_rh.jpg"
  },
  {
    "id": 11,
    "name": "태버사",
    "tier": "S",
    "rarity": "SSR",
    "company": "미샤라",
    "weapon": "AR",
    "element": "수속성",
    "burst": "II",
    "position": "지원형",
    "content": [
      "PVP",
      "유니온"
    ],
    "rating": 4,
    "scores": {
      "story": 3,
      "boss": 3,
      "pvp": 5,
      "raid": 3,
      "union": 4
    },
    "pros": [
      "PVP 필수 서포터",
      "공유 버스트"
    ],
    "cons": [
      "PVE 활용 낮음"
    ],
    "overload": [
      "재장전 속도 ↑"
    ],
    "cube": "재장전 큐브",
    "team": [
      "태버사 · 노아 · 마카롱"
    ],
    "priority": [
      "2스킬 → 3스킬"
    ],
    "reroll": false,
    "history": [
      "S",
      "S",
      "S",
      "S",
      "S",
      "S",
      "S",
      "S"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Tabitha.jpg"
  },
  {
    "id": 14,
    "name": "볼륨",
    "tier": "A",
    "rarity": "SSR",
    "company": "테트라라인",
    "weapon": "MG",
    "element": "철갑탄",
    "burst": "III",
    "position": "화력형",
    "content": [
      "스토리",
      "유니온"
    ],
    "rating": 3,
    "scores": {
      "story": 4,
      "boss": 3,
      "pvp": 2,
      "raid": 3,
      "union": 3
    },
    "pros": [
      "코어 파괴 우수",
      "기재값 낮음"
    ],
    "cons": [
      "광역 부족"
    ],
    "overload": [
      "공격력 ↑"
    ],
    "cube": "탄창 큐브",
    "team": [
      "볼륨 · 크라운"
    ],
    "priority": [
      "3스킬"
    ],
    "reroll": false,
    "history": [
      "A",
      "A",
      "A",
      "A",
      "A",
      "A",
      "A",
      "A"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Volume.jpg"
  },
  {
    "id": 16,
    "name": "센티",
    "tier": "B",
    "rarity": "SSR",
    "company": "핀윙",
    "weapon": "SR",
    "element": "철갑탄",
    "burst": "III",
    "position": "화력형",
    "content": [
      "보스"
    ],
    "rating": 2,
    "scores": {
      "story": 2,
      "boss": 3,
      "pvp": 2,
      "raid": 2,
      "union": 2
    },
    "pros": [
      "단일 딜 안정"
    ],
    "cons": [
      "대체재 많음"
    ],
    "overload": [
      "치명타 피해 ↑"
    ],
    "cube": "재장전 큐브",
    "team": [
      "센추리 · 크라운"
    ],
    "priority": [
      "3스킬"
    ],
    "reroll": false,
    "history": [
      "B",
      "B",
      "B",
      "B",
      "B",
      "B",
      "B",
      "B"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Centi.jpg"
  },
  {
    "id": 17,
    "name": "메리",
    "tier": "A",
    "rarity": "SSR",
    "company": "테트라라인",
    "weapon": "SG",
    "element": "전기",
    "burst": "II",
    "position": "지원형",
    "content": [
      "유니온"
    ],
    "rating": 3,
    "scores": {
      "story": 3,
      "boss": 3,
      "pvp": 3,
      "raid": 3,
      "union": 4
    },
    "pros": [
      "전기 파티 서포터"
    ],
    "cons": [
      "범용성 낮음"
    ],
    "overload": [
      "공격력 ↑"
    ],
    "cube": "탄창 큐브",
    "team": [
      "메리 · 도로시"
    ],
    "priority": [
      "2스킬"
    ],
    "reroll": false,
    "history": [
      "A",
      "A",
      "A",
      "A",
      "A",
      "A",
      "A",
      "A"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Mary.jpg"
  },
  {
    "id": 18,
    "name": "아니스",
    "tier": "B",
    "rarity": "SSR",
    "company": "카운터즈",
    "weapon": "SMG",
    "element": "화염",
    "burst": "III",
    "position": "화력형",
    "content": [
      "스토리"
    ],
    "rating": 2,
    "scores": {
      "story": 2,
      "boss": 2,
      "pvp": 2,
      "raid": 2,
      "union": 2
    },
    "pros": [
      "초반 무난"
    ],
    "cons": [
      "엔드컨텐츠 부족"
    ],
    "overload": [
      "공격력 ↑"
    ],
    "cube": "재장전 큐브",
    "team": [
      "아니스 · 라피"
    ],
    "priority": [
      "3스킬"
    ],
    "reroll": false,
    "history": [
      "B",
      "B",
      "B",
      "B",
      "B",
      "B",
      "B",
      "B"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Anis.jpg"
  },
  {
    "id": 19,
    "name": "네온",
    "tier": "C",
    "rarity": "SSR",
    "company": "카운터즈",
    "weapon": "SG",
    "element": "화염",
    "burst": "II",
    "position": "지원형",
    "content": [
      "스토리"
    ],
    "rating": 2,
    "scores": {
      "story": 2,
      "boss": 1,
      "pvp": 2,
      "raid": 1,
      "union": 2
    },
    "pros": [
      "초반 버스트 순환"
    ],
    "cons": [
      "엔드컨텐츠 부족"
    ],
    "overload": [
      "공격력 ↑"
    ],
    "cube": "탄창 큐브",
    "team": [
      "네온 · 라피"
    ],
    "priority": [
      "2스킬"
    ],
    "reroll": false,
    "history": [
      "C",
      "C",
      "C",
      "C",
      "C",
      "C",
      "C",
      "C"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Neon.jpg"
  },
  {
    "id": 22,
    "name": "루드밀라",
    "tier": "S",
    "rarity": "SSR",
    "company": "핀윙",
    "weapon": "SMG",
    "element": "철갑탄",
    "burst": "I",
    "position": "탱커형",
    "content": [
      "PVP",
      "스토리"
    ],
    "rating": 4,
    "scores": {
      "story": 4,
      "boss": 3,
      "pvp": 5,
      "raid": 3,
      "union": 3
    },
    "pros": [
      "PVP 탱커",
      "도발 유틸"
    ],
    "cons": [
      "PVE 애매"
    ],
    "overload": [
      "방어력 ↑",
      "체력 ↑"
    ],
    "cube": "체력 큐브",
    "team": [
      "루드밀라 · 노아"
    ],
    "priority": [
      "1스킬 → 2스킬"
    ],
    "reroll": false,
    "history": [
      "S",
      "S",
      "S",
      "S",
      "S",
      "S",
      "S",
      "S"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Ludmilla.jpg"
  },
  {
    "id": 23,
    "name": "프리바티",
    "tier": "SS",
    "rarity": "SSR",
    "company": "테트라라인",
    "weapon": "RL",
    "element": "전기",
    "burst": "III",
    "position": "화력형",
    "content": [
      "레이드",
      "보스"
    ],
    "rating": 5,
    "scores": {
      "story": 4,
      "boss": 5,
      "pvp": 3,
      "raid": 5,
      "union": 4
    },
    "pros": [
      "최상위 폭딜",
      "보스 클리어"
    ],
    "cons": [
      "세팅 요구값 큼"
    ],
    "overload": [
      "치명타 피해 ↑",
      "공격력 ↑"
    ],
    "cube": "탄창 큐브",
    "team": [
      "프리바티 · 크라운 · 도로시"
    ],
    "priority": [
      "3스킬 → 2스킬"
    ],
    "reroll": true,
    "history": [
      "SS",
      "SS",
      "SS",
      "SS",
      "SS",
      "SS",
      "SS",
      "SS"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Privaty.jpg"
  },
  {
    "id": 24,
    "name": "라플라스",
    "tier": "A",
    "rarity": "SSR",
    "company": "카운터즈",
    "weapon": "RL",
    "element": "전기",
    "burst": "II",
    "position": "지원형",
    "content": [
      "스토리",
      "유니온"
    ],
    "rating": 3,
    "scores": {
      "story": 3,
      "boss": 3,
      "pvp": 3,
      "raid": 3,
      "union": 3
    },
    "pros": [
      "안정적 버프",
      "전기 시너지"
    ],
    "cons": [
      "티어 인상 필요"
    ],
    "overload": [
      "공격력 ↑"
    ],
    "cube": "재장전 큐브",
    "team": [
      "라플라스 · 크라운"
    ],
    "priority": [
      "2스킬 → 3스킬"
    ],
    "reroll": false,
    "history": [
      "A",
      "A",
      "A",
      "A",
      "A",
      "A",
      "A",
      "A"
    ],
    "image": "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Laplace.jpg"
  }
]"""
FALLBACK = json.loads(FALLBACK_JSON)

def fetch_prydwen():
    url="https://www.prydwen.gg/nikke/tier-list"
    headers={"User-Agent":"Mozilla/5.0"}
    try:
        r=requests.get(url,headers=headers,timeout=20)
        r.raise_for_status()
        soup=BeautifulSoup(r.text,"lxml")
        tag=soup.find("script",id="__NEXT_DATA__")
        tiers={}
        if tag and tag.string:
            jd=json.loads(tag.string)
            def rec(o):
                if isinstance(o,dict):
                    if "name" in o and ("tier" in o or "rating" in o):
                        n=o.get("name"); t=o.get("tier") or o.get("rating")
                        if n and t: tiers[n]=str(t).upper().strip()
                    for v in o.values(): rec(v)
                elif isinstance(o,list):
                    for x in o: rec(x)
            rec(jd)
        return tiers
    except Exception as e:
        print(f"[WARN] fetch fail {e}")
        return {}

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    chars=None
    if os.path.exists(CHAR_FILE):
        try:
            with open(CHAR_FILE,"r",encoding="utf-8") as f:
                d=json.load(f)
                if isinstance(d,list) and len(d)>=5:
                    chars=d
                    print(f"[INFO] loaded {len(d)} chars")
        except Exception as e:
            print(f"[WARN] load fail {e}")
    if not chars:
        print("[INFO] fallback 21개 복구")
        chars=FALLBACK

    raw=fetch_prydwen()
    if raw:
        with open(RAW_FILE,"w",encoding="utf-8") as f: json.dump(raw,f,ensure_ascii=False,indent=2)
    else:
        if os.path.exists(RAW_FILE):
            try:
                with open(RAW_FILE,"r",encoding="utf-8") as f: raw=json.load(f)
            except: raw={}

    changed=[]
    now=datetime.now(timezone.utc)
    kst=datetime.now().astimezone()
    date_str=kst.strftime("%Y-%m-%d")

    for c in chars:
        ko=c["name"]
        en=c.get("en_name") or KO_TO_EN.get(ko) or ko
        new_raw=raw.get(en) or raw.get(ko)
        if not new_raw:
            for k,v in raw.items():
                if k.lower()==en.lower() or k.lower()==ko.lower():
                    new_raw=v; break
        if new_raw:
            nt=PRYDWEN_MAP.get(new_raw.upper(), new_raw.upper())
            ot=c.get("tier","B")
            if nt!=ot and nt in TIER_ORDER:
                orank=TIER_ORDER.get(ot,99); nrank=TIER_ORDER.get(nt,99)
                typ="up" if nrank<orank else "down"
                hist=c.get("history",[]); hist.append(nt); c["history"]=hist[-8:]
                c["tier"]=nt
                c["rating"]=5 if nt in ["SSS","SS"] else 4 if nt=="S" else 3
                changed.append({"id":c["id"],"name":ko,"type":typ,"from":ot,"to":nt})
                print(f"[UPDATE] {ko} {ot}->{nt}")

    with open(CHAR_FILE,"w",encoding="utf-8") as f: json.dump(chars,f,ensure_ascii=False,indent=2)

    counts={"new":0,"up":0,"down":0,"buff":0,"nerf":0}
    for ch in changed: counts[ch["type"]]=counts.get(ch["type"],0)+1

    weekly={
        "date": date_str,
        "metaVersion": f"{kst.strftime('%Y-%m')} 메타",
        "week": f"{kst.strftime('%Y년 %m월 %d일')} 기준",
        "note": f"prydwen.gg 기준 자동 업데이트 - {len(changed)}명 변동",
        "counts": counts,
        "changes": changed,
        "updated_at": now.isoformat(),
        "updated_at_kst": kst.strftime("%Y-%m-%d %H:%M:%S KST"),
        "source": "prydwen.gg",
        "total": len(chars)
    }
    with open(WEEKLY_FILE,"w",encoding="utf-8") as f: json.dump(weekly,f,ensure_ascii=False,indent=2)
    print(f"DONE {len(chars)} chars, changed {len(changed)}")

if __name__=="__main__":
    main()
