"""
prydwen.gg -> characters.json 자동 최신화 크롤러
- prydwen.gg /nikke/tier-list 에서 티어 긁어옴
- 네 characters.json (한글 이름) 과 영문 이름 매핑해서 tier / rating 자동 업데이트
- history 자동 누적 (최대 8개)
- characters.json이 지워져도 fallback에서 복구
"""
import json
import os
import re
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

DATA_DIR = "games/nikke/data"
CHAR_FILE = os.path.join(DATA_DIR, "characters.json")
WEEKLY_FILE = os.path.join(DATA_DIR, "weekly-update.json")
RAW_FILE = os.path.join(DATA_DIR, "prydwen_raw.json")

# 한글 <-> 영문 매핑 (prydwen 영문명 : 한글명)
EN_TO_KO = {
    "Scarlet": "홍련",  # 홍련 = Scarlet 원본, 스칼렛은 별개지만 일단 매핑
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
    "Red Hood: Rapi": "라피 RH",
    "Tabitha": "태버사",
    "Volume": "볼륨",
    "Centi": "센티",
    "Mary": "메리",
    "Anis": "아니스",
    "Neon": "네온",
    "Ludmilla": "루드밀라",
    "Privaty": "프리바티",
    "Laplace": "라플라스",
    "Alice": "앨리스",
    "Snow White": "백설",
    "SBS": "블랙 섀도우",
    "Mast": "마스트",
    "Cinderella": "신데렐라",
    "Grave": "그레이브",
    "Rapunzel": "라푼젤",
    "Marciana": "마르차나",
    "Tia": "티아",
    "Naga": "나가",
    "Ein": "아인",
    "Quency": "퀀시",
}

KO_TO_EN = {v: k for k, v in EN_TO_KO.items()}

# prydwen 티어 텍스트 -> 네 티어 시스템 변환
PRYDWEN_TIER_MAP = {
    "SSS": "SSS", "SS": "SS", "S": "S", "A": "A", "B": "B", "C": "C", "D": "C", "E": "C", "F": "C",
    "0": "SSS", "1": "SS", "2": "S", "3": "A", "4": "B", "5": "C"
}

def fetch_prydwen_tiers():
    """
    prydwen.gg 에서 티어 긁기. 3단계로 시도
    """
    url = "https://www.prydwen.gg/nikke/tier-list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9,ko;q=0.8"
    }
    print(f"[INFO] Fetching {url}")
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    html = resp.text

    # 1) __NEXT_DATA__ 파싱 시도
    try:
        soup = BeautifulSoup(html, "lxml")
        next_data_tag = soup.find("script", id="__NEXT_DATA__")
        if next_data_tag and next_data_tag.string:
            data = json.loads(next_data_tag.string)
            # 재귀적으로 tier 정보 찾기
            tiers = {}
            def recurse(obj):
                if isinstance(obj, dict):
                    # 캐릭터 객체 패턴: {name: "Scarlet", tier: "SSS" ...}
                    if "name" in obj and ("tier" in obj or "rating" in obj):
                        name = obj.get("name")
                        tier = obj.get("tier") or obj.get("rating") or obj.get("rank")
                        if name and tier:
                            # tier가 리스트일 수도 있음
                            if isinstance(tier, str):
                                tier = tier.strip().upper()
                            tiers[name] = tier
                    for v in obj.values():
                        recurse(v)
                elif isinstance(obj, list):
                    for item in obj:
                        recurse(item)
            recurse(data)
            if tiers:
                print(f"[INFO] __NEXT_DATA__에서 {len(tiers)}개 티어 발견")
                return tiers
    except Exception as e:
        print(f"[WARN] __NEXT_DATA__ 파싱 실패: {e}")

    # 2) HTML 구조 파싱 (Tier 섹션별)
    try:
        soup = BeautifulSoup(html, "lxml")
        tiers = {}
        # prydwen은 보통 h3에 SSS, SS, S... 그리고 그 아래에 캐릭터 아이콘
        # 모든 텍스트 노드에서 티어 라벨 찾기
        tier_labels = ["SSS", "SS", "S", "A", "B", "C", "D", "E", "F"]
        current_tier = None
        for elem in soup.find_all(["h2", "h3", "h4", "div", "span"]):
            text = elem.get_text(strip=True).upper()
            if text in tier_labels:
                current_tier = text
                continue
            # 캐릭터 이름이 alt나 title에 있음
            if current_tier:
                # img alt
                imgs = elem.find_all("img", alt=True)
                for img in imgs:
                    name = img["alt"].strip()
                    if name and len(name) < 40:
                        tiers[name] = current_tier
        if tiers:
            print(f"[INFO] HTML 구조 파싱에서 {len(tiers)}개 발견")
            return tiers
    except Exception as e:
        print(f"[WARN] HTML 파싱 실패: {e}")

    # 3) 정규식으로 fallback
    try:
        # 예: "Scarlet - SSS" 패턴
        matches = re.findall(r'"name"\s*:\s*"([^"]+)"[^}]{0,200}"tier"\s*:\s*"([A-Z0-9]+)"', html)
        if matches:
            tiers = {name: tier for name, tier in matches}
            print(f"[INFO] Regex로 {len(tiers)}개 발견")
            return tiers
    except Exception as e:
        print(f"[WARN] Regex 실패: {e}")

    raise ValueError("prydwen.gg 티어 데이터를 찾을 수 없습니다. 구조가 바뀌었을 수 있습니다.")

def load_characters():
    if os.path.exists(CHAR_FILE):
        try:
            with open(CHAR_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    print(f"[INFO] 기존 파일 로드: {len(data)}명")
                    return data
        except Exception as e:
            print(f"[WARN] 기존 파일 로드 실패: {e}")
    # fallback 없음 -> 빈 리스트로 시작 (prydwen에서 새로 만들 수도 있음)
    print("[WARN] characters.json 없음, 빈 리스트로 시작 (prydwen 데이터로 채울 예정)")
    return []

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 저장: {path}")

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. prydwen에서 최신 티어 가져오기
    try:
        raw_tiers = fetch_prydwen_tiers()
        save_json(RAW_FILE, raw_tiers)
    except Exception as e:
        print(f"[ERROR] prydwen fetch 실패, 기존 데이터 유지: {e}")
        raw_tiers = {}
        if os.path.exists(RAW_FILE):
            try:
                with open(RAW_FILE, "r", encoding="utf-8") as f:
                    raw_tiers = json.load(f)
            except:
                pass

    # 2. 기존 캐릭터 로드
    characters = load_characters()

    # 만약 characters.json이 완전히 비어있으면 fallback: prydwen 이름으로 기본 객체 생성
    if not characters and raw_tiers:
        print("[INFO] characters.json이 비어있어서 prydwen 기준으로 새로 생성")
        for en_name, tier in raw_tiers.items():
            ko_name = EN_TO_KO.get(en_name, en_name)
            tier = PRYDWEN_TIER_MAP.get(tier.upper(), tier)
            characters.append({
                "id": len(characters)+1,
                "name": ko_name,
                "en_name": en_name,
                "tier": tier,
                "rarity": "SSR",
                "history": [tier],
                "image": f"https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/{en_name.replace(':', '').replace(' ', '_')}.jpg"
            })

    # 3. 병합 (티어 업데이트)
    changed = []
    for char in characters:
        ko_name = char.get("name")
        en_name = char.get("en_name") or KO_TO_EN.get(ko_name) or ko_name

        # prydwen에서 이 캐릭터의 티어 찾기 (영문, 한글 둘 다 시도)
        new_tier_raw = raw_tiers.get(en_name) or raw_tiers.get(ko_name)
        if not new_tier_raw:
            # 대소문자 무시 검색
            for k, v in raw_tiers.items():
                if k.lower() == en_name.lower() or k.lower() == ko_name.lower():
                    new_tier_raw = v
                    break

        if new_tier_raw:
            new_tier = PRYDWEN_TIER_MAP.get(str(new_tier_raw).upper(), str(new_tier_raw).upper())
            old_tier = char.get("tier", "B")
            if new_tier != old_tier:
                changed.append({"name": ko_name, "en": en_name, "from": old_tier, "to": new_tier})
                # history 관리
                hist = char.get("history", [])
                if not hist or hist[-1] != old_tier:
                    hist.append(old_tier)
                hist.append(new_tier)
                if len(hist) > 8:
                    hist = hist[-8:]
                char["history"] = hist
                char["tier"] = new_tier
                # rating도 티어 기반으로 자동 보정 (원하면 유지)
                tier_to_rating = {"SSS": 5, "SS": 5, "S": 4, "A": 3, "B": 2, "C": 1}
                char["rating"] = tier_to_rating.get(new_tier, char.get("rating", 3))
                print(f"[UPDATE] {ko_name} ({en_name}): {old_tier} -> {new_tier}")

    # 4. 저장
    save_json(CHAR_FILE, characters)

    weekly = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_at_kst": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S KST"),
        "source": "prydwen.gg",
        "total": len(characters),
        "fetched": len(raw_tiers),
        "changed": changed,
        "changed_count": len(changed)
    }
    save_json(WEEKLY_FILE, weekly)

    # gitkeep
    gitkeep = os.path.join(DATA_DIR, ".gitkeep")
    if not os.path.exists(gitkeep):
        open(gitkeep, "w").close()

    print(f"\n=== 완료: {len(characters)}명, 변경 {len(changed)}명 ===")

if __name__ == "__main__":
    main()