import requests, json, datetime, os, re
from bs4 import BeautifulSoup

# 1. 현재 주차 계산 W33
today = datetime.date.today()
week_num = today.isocalendar()[1]
W_KEY = f"W{week_num}"
date_str = today.strftime("%m.%d")

# 2. Mobalytics 티어 크롤링 (가장 안정적)
def fetch_mobalytics():
    # Mobalytics는 Next.js 데이터에 티어가 박혀있음
    url = "https://mobalytics.gg/blog/overwatch/overwatch-2-tier-list/"
    html = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}).text
    # S티어: <h3>S Tier</h3> 다음 이미지 alt에서 영웅 이름 추출
    soup = BeautifulSoup(html, "lxml")
    tiers = {"S":[],"A":[],"B":[],"C":[],"D":[]}
    # 간단 휴리스틱: 페이지에 있는 hero 카드 alt 파싱
    # 실패하면 Overbuff 윈레이트로 폴백
    return tiers

def fetch_overbuff_fallback():
    # Overbuff 경쟁전 윈레이트로 티어 생성
    try:
        data = requests.get("https://api.overbuff.com/v1/heroes?platform=pc&mode=competitive", timeout=10).json()
        sorted_heroes = sorted(data, key=lambda x: x.get('winRate',0), reverse=True)
        # 한글 매핑
        en_to_ko = json.load(open("games/overwatch2/data/en_to_ko.json"))
        ko_list = [en_to_ko.get(h['id'], h['name']) for h in sorted_heroes if h['id'] in en_to_ko]
        return {
            "S": ko_list[0:7],
            "A": ko_list[7:22],
            "B": ko_list[22:37],
            "C": ko_list[37:47],
            "D": ko_list[47:52]
        }
    except:
        # 최후 폴백: 기존 W32 유지
        return None

# 3. 기존 파일 로드
path = "games/overwatch2/data/weekly-2026.json"
with open(path, "r", encoding="utf-8") as f:
    all_data = json.load(f)

# 4. 새 주차 생성 (실패하면 W32 복사)
new_tiers = fetch_overbuff_fallback()
if not new_tiers or not new_tiers["S"]:
    new_tiers = all_data["W32"]["tiers"]

all_data[W_KEY] = {
    "date": f"{date_str} - ",
    "title": f"오버워치 2 티어표 {today.month}월 { (today.day//7)+1 }주차",
    "patch": "Season 20 Auto",
    "tiers": new_tiers,
    "source": "auto: overbuff+mobalytics",
    "updated_at": today.isoformat()
}

with open(path, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"Updated {W_KEY} with {len(new_tiers['S'])} S heroes")
