import json, datetime, os, sys
import requests

# 경로 자동 계산 (어디서 실행되든 되게)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../"))
DATA_PATH = os.path.join(ROOT, "games/overwatch2/data/weekly-2026.json")
ENKO_PATH = os.path.join(ROOT, "games/overwatch2/data/en_to_ko.json")

print(f"DATA_PATH: {DATA_PATH}")
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

# 1. 주차 계산
today = datetime.date.today()
week_num = today.isocalendar()[1]
W_KEY = f"W{week_num}"
date_str = today.strftime("%m.%d")

# 2. 기존 파일 없으면 W32 기본값으로 생성 (52명)
DEFAULT_W32 = {
  "W32": {
    "date": "07.30 - 08.05",
    "title": "오버워치 2 티어표 8월 1주차",
    "patch": "Season 20 - Vendetta",
    "tiers": {
      "S": ["트레이서","겐지","소전","자리야","시그마","디바","키리코","루시우"],
      "A": ["애쉬","솔저:76","파라","프레야","리퍼","캐서디","벤데타","둠피스트","정커퀸","라마트라","윈스턴","레킹볼","주노","바티스트","브리기테","우양","시온","제트팩 캣"],
      "B": ["바스티온","정크랫","메이","시메트라","솜브라","한조","에코","벤처","위도우메이커","오리사","해저드","마우가","일리아리","아나","안란","시에라","도미나","엠레","미즈키"],
      "C": ["토르비욘","로드호그","젠야타","메르시","모이라"],
      "D": ["라인하르트","라이프위버"]
    },
    "source": "init 52 heroes"
  }
}

all_data = {}
if os.path.exists(DATA_PATH):
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            all_data = json.load(f)
    except:
        all_data = DEFAULT_W32
else:
    all_data = DEFAULT_W32

# 3. 이번주 데이터 만들기 (없으면 W32 복사)
if W_KEY not in all_data:
    # Overbuff 폴백 시도 (실패해도 W32 복사라 안전)
    try:
        # en_to_ko 없으면 기본 맵 생성
        en_to_ko = {}
        if os.path.exists(ENKO_PATH):
            with open(ENKO_PATH, "r", encoding="utf-8") as f:
                en_to_ko = json.load(f)

        # W32 복사해서 날짜만 갱신 (크롤링 실패해도 500 안나게)
        last_key = list(all_data.keys())[-1]
        new_tiers = all_data[last_key]["tiers"]
    except Exception as e:
        print(f"fallback error {e}")
        new_tiers = DEFAULT_W32["W32"]["tiers"]

    all_data[W_KEY] = {
        "date": f"{date_str} - ",
        "title": f"오버워치 2 티어표 {today.month}월 {(today.day//7)+1}주차",
        "patch": "Season 20 Auto",
        "tiers": new_tiers,
        "source": "auto: copy last week",
        "updated_at": today.isoformat()
    }
    print(f"Created {W_KEY}")

# 4. 저장
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"Success: {list(all_data.keys())[-3:]}")
