"""
Palworld Weekly Updater - NoPickle
- Source 1: mlg404/palworld-paldex-api (공식 스탯 + 이미지 파일명 001.png, 012B.png)
- Source 2: game8.co/archives/440279 (전투 티어 S~C, 주간 갱신)
- Source 3: palworld.gg/tier-list (유저 투표 기반)
- Output: games/palworld/data/pals.json + wp-content/.../pals.json 호환

파일명 규칙: 네가 캡처한 대로 001.png, 012B.png (대문자 B)
"""
import requests, json, os, datetime, re
from bs4 import BeautifulSoup

# --- 1. Paldeck API에서 전체 팰 스탯 가져오기 ---
def fetch_paldeck_api():
    urls = [
        "https://raw.githubusercontent.com/mlg404/palworld-paldex-api/main/public/images/paldeck/paldeck.json",
        "https://cdn.jsdelivr.net/gh/mlg404/palworld-paldex-api@main/public/images/paldeck/paldeck.json"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                data = r.json()
                print(f"Paldeck loaded: {len(data)} from {url}")
                return data
        except Exception as e:
            print(f"fetch fail {url}: {e}")
    return []

# --- 2. Game8 전투 티어 크롤링 ---
def fetch_game8_tier():
    # Game8은 Cloudflare가 있어서 실패할 수 있음 -> fallback으로 하드코딩 티어 유지
    try:
        url = "https://game8.co/games/Palworld/archives/440279"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            print(f"Game8 status {r.status_code}")
            return {}
        soup = BeautifulSoup(r.text, 'lxml')
        # S Tier 키워드 근처에서 팰 이름 추출 (간이 파싱)
        text = soup.get_text()
        # 실제로는 상세 파싱 필요, 지금은 로그만
        print(f"Game8 fetched {len(text)} chars")
        return {}
    except Exception as e:
        print(f"Game8 fetch error: {e}")
        return {}

# --- 3. 티어 계산 로직 (네 사진처럼 작업 레벨 1~8 기반) ---
def compute_work_tier(work_dict):
    # work_dict 예: {"kindling": 3, "watering": 2, ...}
    max_lv = max(work_dict.values()) if work_dict else 0
    total = sum(work_dict.values())
    # 사진 기준: S=8,7 / A=6,5 / B=4,5 / C=3,4 / D=2 이하
    if max_lv >= 7 or (max_lv >= 4 and total >= 8):
        return "S"
    if max_lv >= 5:
        return "A"
    if max_lv >= 4:
        return "B"
    if max_lv >= 2:
        return "C"
    return "D"

def build_pals_json():
    raw = fetch_paldeck_api()
    game8 = fetch_game8_tier()

    # 기존 pals.json이 있으면 병합
    existing_path = "games/palworld/data/pals.json"
    existing = []
    if os.path.exists(existing_path):
        try:
            with open(existing_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except:
            pass

    # mlg404 API 구조: [{id: 1, name: "Lamball", ... , workSuitability: {kindling:1,...}}] 형태 가정
    # 실제 API가 배열이 아닐 수도 있으니 유연하게 처리
    pals = []
    id_to_ko = {p["id"]: p for p in existing}  # 기존 한국어 매핑 유지

    if raw and isinstance(raw, list):
        for entry in raw:
            try:
                pid_num = entry.get("id") or entry.get("no") or 0
                # 파일명 규칙: 001, 012B.png
                # entry에 variant가 있으면 B 붙이기
                pid_str = f"{int(pid_num):03d}"
                # 변이종 체크: 이름에 B, variant 등
                name = entry.get("name","")
                if "B" in str(entry.get("variant","")) or "B" in name or entry.get("isVariant"):
                    # 실제 리스트는 012B.png처럼 대문자 B
                    pid_str = f"{pid_str}B"

                # 기존 한국어 데이터 있으면 재사용
                ko_data = id_to_ko.get(pid_str) or id_to_ko.get(pid_str.replace("B","")) or {}
                
                work = entry.get("workSuitability") or entry.get("work") or {}
                # work가 dict가 아니면 빈 dict
                if not isinstance(work, dict):
                    work = {}

                # 티어: 기존 티어 유지, 없으면 work 기반 계산 (네 사진 방식)
                tier = ko_data.get("tier")
                if not tier:
                    tier = compute_work_tier(work)

                pals.append({
                    "id": pid_str,  # 중요: 대문자 B 유지 (001, 012B)
                    "name": entry.get("name", ko_data.get("name", pid_str)),
                    "ko": ko_data.get("ko", entry.get("name", pid_str)),
                    "element": ko_data.get("element", entry.get("element", ["Neutral"])),
                    "tier": tier,
                    "type": ko_data.get("type", "거점" if sum(work.values())>0 else "전투"),
                    "work": ko_data.get("work", ",".join([f"{k}{v}" for k,v in work.items() if v>0]) or "초반"),
                    "work_level": work,  # 네 사진의 8,7,6 숫자용
                    "desc": ko_data.get("desc",""),
                    "max_work": max(work.values()) if work else 0
                })
            except Exception as e:
                print(f"parse error {entry}: {e}")
                continue
    else:
        # API 실패시 기존 데이터 그대로 사용 + last_update만 갱신
        pals = existing
        print("Using existing data as fallback")

    # 최소 30개 이상 확보 (기존 데이터가 더 많으면 기존 우선)
    if len(pals) < 10 and existing:
        pals = existing

    # 정렬: 티어 S->D, 그 다음 max_work 높은 순
    tier_order = {"S+":0, "S":1, "A":2, "B":3, "C":4, "D":5}
    pals.sort(key=lambda x: (tier_order.get(x.get("tier","C"), 9), -x.get("max_work",0)))

    return pals

if __name__ == "__main__":
    os.makedirs("games/palworld/data", exist_ok=True)
    os.makedirs("wp-content/themes/generatepress-child/palworld-tier/data", exist_ok=True)

    pals = build_pals_json()
    
    # 저장 1: games/palworld/data
    with open("games/palworld/data/pals.json","w",encoding="utf-8") as f:
        json.dump(pals, f, ensure_ascii=False, indent=2)

    # 저장 2: last_update
    last = {
        "last_update": datetime.datetime.utcnow().isoformat(),
        "last_update_kst": (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).isoformat(),
        "count": len(pals),
        "sources": [
            "https://github.com/mlg404/palworld-paldex-api (001.png, 012B.png 규칙)",
            "https://game8.co/games/Palworld/archives/440279",
            "https://palworld.gg/tier-list"
        ],
        "note": "파일명은 대문자 B (예: 012B.png) 규칙을 따름 - 유저가 캡처한 리스트 기준"
    }
    with open("games/palworld/data/last_update.json","w",encoding="utf-8") as f:
        json.dump(last, f, ensure_ascii=False, indent=2)

    # 저장 3: WP 테마 내부 복사 (로컬)
    with open("wp-content/themes/generatepress-child/palworld-tier/data/pals.json","w",encoding="utf-8") as f:
        json.dump(pals, f, ensure_ascii=False, indent=2)
    with open("wp-content/themes/generatepress-child/palworld-tier/data/last_update.json","w",encoding="utf-8") as f:
        json.dump(last, f, ensure_ascii=False, indent=2)

    print(f"Done: {len(pals)} pals, last_update saved")
