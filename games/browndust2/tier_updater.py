#!/usr/bin/env python3
# games/browndust2/tier_updater.py - v5: 실제 티어 크롤링 + KST + characters.json 최신화
import json
import re
import os
import requests
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"

KST = ZoneInfo("Asia/Seoul")
now_kst = datetime.now(KST)

print(f"[BD2] KST: {now_kst.isoformat()}")

# 티어 순서 정의 (높을수록 강함)
TIER_ORDER = {"SS+": 6, "SS": 5, "S": 4, "A": 3, "B": 2, "C": 1, "D": 0}

# 영문명 -> id 매핑 (prydwen/pockettactics 영문명과 우리 id 연결)
# 우리 characters.json은 한글이지만 영문명으로도 매칭 가능하도록
NAME_MAP = {
    "helena": ["helena"],
    "eclipse": ["eclipse"],
    "diana": ["diana", "magical innovator diana"],
    "lathel": ["lathel"],
    "celia": ["celia", "the descendant of the great witch celia"],
    "scheherazade": ["scheherazade", "schera"],
    "rafine": ["rafina", "rafine"],
    "terisse": ["teresse", "terisse", "beachside angel teresse"],
    "rou": ["rou"],
    "kry": ["kry"],
    "angelica": ["angelica"],
    "justia": ["justia", "pool party justia", "sacred justia"],
    "olstein": ["olstein"],
    "seir": ["seir", "new hire seir"],
    "elpis": ["elpis"],
    "sylvia": ["sylvia", "bikini agent sylvia", "deserted flower sylvia"],
    "alec": ["alec"],
    "lucrezia": ["lucrezia"],
    # 추가 확장 가능
    "liatris": ["liatris"],
    "arines": ["arines"],
    "samay": ["samay"],
    "morpeah": ["morpeah"],
    "yuri": ["yuri"],
    "levia": ["levia"],
    "lecliss": ["lecliss"],
    "lydia": ["lydia"],
}

# 역 매핑: 영문명(lower) -> id
REVERSE_MAP = {}
for cid, aliases in NAME_MAP.items():
    for alias in aliases:
        REVERSE_MAP[alias.lower()] = cid

def load_json(path, default):
    if not path.exists():
        return default
    try:
        if path.stat().st_size == 0:
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[BD2] load fail {path}: {e}")
        return default

def fetch_pockettactics():
    """pockettactics.com에서 S/A/B/C 리스트 파싱"""
    url = "https://www.pockettactics.com/brown-dust-2/tier-list"
    headers = {"User-Agent": "Mozilla/5.0 (BD2-tier-bot)"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text(" ", strip=True).lower()

        # 정규식으로 Tier 추출 - | S | ... | 형태
        # 페이지에 테이블로 되어있음, get_text로 합쳐져도 패턴 유지
        tiers = {"S": [], "A": [], "B": [], "C": [], "D": []}
        
        # 전체 텍스트에서 S/A/B/C 구분
        # 방법: HTML 원문에서 파이프 테이블 찾기
        raw = r.text
        # | S | ... | 패턴
        pattern = r"\|\s*([SABCD])\s*\|\s*([^|]+?)\s*\|"
        matches = re.findall(pattern, raw, re.IGNORECASE)
        print(f"[BD2] Found {len(matches)} tier rows from raw")
        for tier_letter, names_blob in matches:
            tier_letter = tier_letter.upper()
            if tier_letter not in tiers:
                continue
            # 쉼표로 분리
            names = [n.strip().lower() for n in names_blob.split(",")]
            tiers[tier_letter].extend([n for n in names if n])
        
        # fallback: soup에서 표 찾기
        if not any(tiers.values()):
            for table in soup.find_all("table"):
                rows = table.find_all("tr")
                for row in rows[1:]:
                    cols = row.find_all(["td","th"])
                    if len(cols) >= 2:
                        t = cols[0].get_text(strip=True).upper()
                        if t in tiers:
                            names = [n.strip().lower() for n in cols[1].get_text().split(",")]
                            tiers[t].extend(names)

        print(f"[BD2] Parsed tiers: S={len(tiers['S'])}, A={len(tiers['A'])}, B={len(tiers['B'])}, C={len(tiers['C'])}")
        return tiers
    except Exception as e:
        print(f"[BD2] fetch failed: {e}")
        return None

def tier_letter_to_our_tier(letter):
    mapping = {
        "S": "SS+",
        "A": "SS",
        "B": "S",
        "C": "A",
        "D": "B",
    }
    return mapping.get(letter, "B")

def main():
    characters = load_json(CHAR_PATH, [])
    weekly = load_json(WEEKLY_PATH, {})

    if not characters:
        print("[BD2] characters.json 비어있음 - 복구 필요")
        return

    print(f"[BD2] 기존 {len(characters)}개 로드")

    # 크롤링
    tiers = fetch_pockettactics()
    if not tiers:
        print("[BD2] 크롤링 실패 - 시간만 갱신하고 종료")
        # 시간만 갱신
        iso_year, iso_week, _ = now_kst.isocalendar()
        week_of_month = (now_kst.day - 1) // 7 + 1
        new_weekly = {
            **weekly,
            "version": f"{now_kst.year}년 {now_kst.month:02d}월 {week_of_month}주차 (W{iso_week})",
            "updated": now_kst.strftime("%Y-%m-%d"),
            "updated_at": now_kst.isoformat(),
            "deployed_at": now_kst.isoformat(),
            "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
            "github_sha": os.environ.get("GITHUB_SHA", ""),
        }
        with open(WEEKLY_PATH, "w", encoding="utf-8") as f:
            json.dump(new_weekly, f, ensure_ascii=False, indent=2)
        return

    # 기존 캐릭터 맵
    char_map = {c["id"]: c for c in characters}

    buff = []
    nerf = []

    # 티어 적용
    for tier_letter, name_list in tiers.items():
        our_tier = tier_letter_to_our_tier(tier_letter)
        for eng_name in name_list:
            eng_name = eng_name.strip().lower()
            # 완전 일치 또는 포함 매칭
            cid = REVERSE_MAP.get(eng_name)
            if not cid:
                # 부분 일치 검색 (예: "magical innovator diana" 안에 "diana" 포함)
                for alias, mapped_id in REVERSE_MAP.items():
                    if alias in eng_name or eng_name in alias:
                        cid = mapped_id
                        break
            if not cid:
                continue
            if cid not in char_map:
                continue

            char = char_map[cid]
            old_tier = char.get("tier", "B")
            old_order = TIER_ORDER.get(old_tier, 0)
            new_order = TIER_ORDER.get(our_tier, 0)

            if old_tier != our_tier:
                print(f"[BD2] {cid} {old_tier} -> {our_tier} (source {tier_letter})")
                # buff/nerf 판정
                if new_order > old_order:
                    buff.append({"id": cid, "name": char.get("name", cid), "from": old_tier, "to": our_tier})
                elif new_order < old_order:
                    nerf.append({"id": cid, "name": char.get("name", cid), "from": old_tier, "to": our_tier})

                char["tier"] = our_tier
                char["grade"] = our_tier
                char["updatedAt"] = now_kst.strftime("%Y-%m-%d")

    # 결과 저장
    # 리스트를 tier 순서대로 정렬
    def sort_key(c):
        return (-TIER_ORDER.get(c.get("tier", "B"), 0), c.get("name", ""))

    characters_sorted = sorted(characters, key=sort_key)

    with open(CHAR_PATH, "w", encoding="utf-8") as f:
        json.dump(characters_sorted, f, ensure_ascii=False, indent=2)
    print(f"[BD2] Saved {CHAR_PATH} - buff {len(buff)} nerf {len(nerf)}")

    iso_year, iso_week, _ = now_kst.isocalendar()
    week_of_month = (now_kst.day - 1) // 7 + 1

    new_weekly = {
        **weekly,
        "version": f"{now_kst.year}년 {now_kst.month:02d}월 {week_of_month}주차 (W{iso_week})",
        "updated": now_kst.strftime("%Y-%m-%d"),
        "updated_at": now_kst.isoformat(),
        "deployed_at": now_kst.isoformat(),
        "meta": f"자동 업데이트 - S:{len(tiers['S'])} A:{len(tiers['A'])} B:{len(tiers['B'])} C:{len(tiers['C'])}",
        "buff": buff,
        "nerf": nerf,
        "note": f"{now_kst.strftime('%m/%d')} 크롤링 기준 티어 반영",
        "banner": weekly.get("banner", ""),
        "headline": weekly.get("headline", weekly.get("banner", "")),
        "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "github_sha": os.environ.get("GITHUB_SHA", ""),
    }

    with open(WEEKLY_PATH, "w", encoding="utf-8") as f:
        json.dump(new_weekly, f, ensure_ascii=False, indent=2)
    print(f"[BD2] Saved weekly: {new_weekly['version']}")

if __name__ == "__main__":
    main()
