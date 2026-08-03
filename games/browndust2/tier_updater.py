#!/usr/bin/env python3
# games/browndust2/tier_updater.py - v6: 신캐 자동 추가 + 한글 이름 강제
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

TIER_ORDER = {"SS+": 6, "SS": 5, "S": 4, "A": 3, "B": 2, "C": 1, "D": 0}

# 영문 -> 한글 이름 매핑 (신캐 포함)
KO_NAME = {
    # 기존 18개
    "helena": "헬레나", "eclipse": "이클립스", "diana": "디아나", "lathel": "라텔",
    "celia": "셀리아", "scheherazade": "셰헤라자드", "schera": "셰헤라자드",
    "rafina": "라피네", "rafine": "라피네", "teresse": "테리스", "terisse": "테리스",
    "rou": "루", "kry": "크라이", "angelica": "안젤리카", "justia": "유스티아",
    "olstein": "올스테인", "seir": "세이르", "elpis": "엘피스", "sylvia": "실비아",
    "alec": "알렉", "lucrezia": "루크레치아",
    # 신캐 S/A/B/C에서 나오는 애들
    "morpeah": "모르페아", "apostle blade": "사도 블레이드", "nebris": "네브리스",
    "beachside justice michaela": "해변의 정의 미카엘라", "venaka": "베나카",
    "liatris": "리아트리스", "levia": "레비아", "loen": "로엔", "yuri": "유리",
    "samay": "사메이", "dark saintess liberta": "암흑 성녀 리베르타",
    "sentana": "센타나", "young lady blade": "영애 블레이드",
    "poolside fairy refithea": "풀사이드 요정 레피테아", "refithea": "레피테아",
    "luvencia": "루벤시아", "acting archbishop michaela": "대행 대주교 미카엘라",
    "michaela": "미카엘라", "earth mother believer priestess": "대지의 무녀",
    "bikini agent sylvia": "비키니 요원 실비아", "beachside angel teresse": "해변의 천사 테리스",
    "shadowed dream sonya": "그림자 꿈 소냐", "sonya": "소냐",
    "magical innovator diana": "마법 혁신가 디아나", "deadeye nekyndalia": "데드아이 네킨달리아",
    "nekyndalia": "네킨달리아", "new hire seir": "신입 세이르", "wiggle": "위글",
    "dalvi": "달비", "yumi": "유미", "roxy": "록시", "rubia": "루비아",
    "elise": "엘리스", "anastasia": "아나스타샤", "eris": "에리스", "gray": "그레이",
    "labyrinth gatekeeper nebris": "미궁 수문장 네브리스", "hikage": "히카게",
    "elaneer": "엘라니어", "onsen manager liberta": "온천 관리자 리베르타",
    "sacred justia": "성스러운 유스티아", "onsen practitioner ventana": "온천 수행가 벤타나",
    "ventana": "벤타나", "daughter of starwind high elf archer": "별바람의 하이엘프 궁수",
    "deserted flower sylvia": "사막의 꽃 실비아", "iron monarch wilhelmina": "철의 군주 빌헬미나",
    "wilhelmina": "빌헬미나", "prophetic dream darian": "예지몽 다리안", "darian": "다리안",
    "starlight guardian tyr": "별빛 수호자 티르", "boo ghost granhildr": "부끄고스트 그란힐드르",
    "granhildr": "그란힐드르", "little pumpkin girl sonya": "꼬마 호박 소녀 소냐",
    "ocean vanguard luvencia": "해양 선봉 루벤시아", "yozakura": "요자쿠라",
    "pool party justia": "풀파티 유스티아", "nartas": "나르타스", "yomi": "요미",
    "rignette": "리넷", "bright moon dalvi": "명월 달비", "fred": "프레드",
    "the descendant of the great witch celia": "대마녀의 후예 셀리아",
    "maid bikini rubia": "메이드 비키니 루비아", "water park queen wilhelmina": "워터파크 여왕 빌헬미나",
    "goblin slayer": "고블린 슬레이어", "tricky lover dalvi": "장난스러운 연인 달비",
    "lecliss": "레클리스", "lydia": "리디아", "bernie": "버니",
    # 추가
    "arines": "아리네스", "liberta": "리베르타", "liberty": "리베르타",
}

def ko_name_of(eng):
    eng_low = eng.lower().strip()
    if eng_low in KO_NAME:
        return KO_NAME[eng_low]
    # 부분 매칭: "beachside justice michaela" -> "michaela" 포함되면 미카엘라
    for k, v in KO_NAME.items():
        if k in eng_low or eng_low in k:
            # 긴 키 우선
            if len(k) > 3:
                return v
    # fallback: 첫 글자 대문자 영문 -> 한글로 그냥 영문 반환 방지, 영문을 한글 음차 대충
    return eng.title()  # 최후 fallback, 이후 수동 수정 필요

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s or "unknown"

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

def fetch_tiers():
    url = "https://www.pockettactics.com/brown-dust-2/tier-list"
    headers = {"User-Agent": "Mozilla/5.0 BD2-bot"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        raw = r.text
        tiers = {"S": [], "A": [], "B": [], "C": []}
        pattern = r"\|\s*([SABCD])\s*\|\s*([^|]+?)\s*\|"
        matches = re.findall(pattern, raw, re.IGNORECASE)
        for tier_letter, names_blob in matches:
            tier_letter = tier_letter.upper()
            if tier_letter not in tiers:
                continue
            names = [n.strip() for n in names_blob.split(",") if n.strip()]
            tiers[tier_letter].extend(names)
        print(f"[BD2] 크롤링 성공: S={len(tiers['S'])} A={len(tiers['A'])} B={len(tiers['B'])} C={len(tiers['C'])}")
        return tiers
    except Exception as e:
        print(f"[BD2] 크롤링 실패: {e}")
        return None

def tier_letter_to_our(letter):
    return {"S": "SS+", "A": "SS", "B": "S", "C": "A", "D": "B"}.get(letter, "B")

def main():
    characters = load_json(CHAR_PATH, [])
    weekly = load_json(WEEKLY_PATH, {})

    if not characters:
        print("[BD2] characters.json 없음 - 새로 생성")
        characters = []

    char_by_id = {c["id"]: c for c in characters}
    # 영문 alias로도 찾기 위해 이름 기반 인덱스
    char_by_eng = {}
    for c in characters:
        # id 기반
        char_by_eng[c["id"].lower()] = c
        # 영문 costume이나 이름에 포함된 영문도 매핑
        eng = c.get("name_en", "").lower()
        if eng:
            char_by_eng[eng] = c

    tiers = fetch_tiers()
    if not tiers:
        print("[BD2] 티어 데이터 못 가져옴 - 종료")
        return

    buff, nerf, new_chars = [], [], []

    for tier_letter, eng_names in tiers.items():
        our_tier = tier_letter_to_our(tier_letter)
        for eng_raw in eng_names:
            eng_raw = eng_raw.strip()
            if not eng_raw:
                continue
            eng_low = eng_raw.lower()
            ko = ko_name_of(eng_raw)

            # 기존 캐릭터 매칭 시도
            matched = None
            # 1) KO_NAME 역매핑으로 id 찾기
            # 영문 전체가 키에 있으면
            if eng_low in KO_NAME:
                # KO_NAME 키로부터 id 유추
                base_id = eng_low.split()[-1]  # 마지막 단어가 base일 가능성
                # 정확히 일치하는 id가 있는지
                for cid in char_by_id:
                    if cid in eng_low or eng_low in cid or KO_NAME.get(cid, "").lower() == ko.lower():
                        matched = char_by_id[cid]
                        break
            # 2) alias 포함 매칭
            if not matched:
                for alias, mapped_ko in KO_NAME.items():
                    if alias in eng_low and mapped_ko == ko:
                        # alias가 포함되면 해당 base id 찾기
                        base = alias.split()[-1]
                        if base in char_by_id:
                            matched = char_by_id[base]
                            break
                        # 또는 ko 이름이 같은 캐릭터
                        for c in characters:
                            if c.get("name") == ko:
                                matched = c
                                break

            # 3) 이미 있는 캐릭터 중 한글 이름이 같은 경우
            if not matched:
                for c in characters:
                    if c.get("name") == ko:
                        matched = c
                        break

            if matched:
                old_tier = matched.get("tier", "B")
                if old_tier != our_tier:
                    print(f"[BD2] 업데이트: {matched['name']} ({matched['id']}) {old_tier} -> {our_tier} [{eng_raw}]")
                    if TIER_ORDER.get(our_tier, 0) > TIER_ORDER.get(old_tier, 0):
                        buff.append({"id": matched["id"], "name": matched["name"], "from": old_tier, "to": our_tier})
                    else:
                        nerf.append({"id": matched["id"], "name": matched["name"], "from": old_tier, "to": our_tier})
                    matched["tier"] = our_tier
                    matched["grade"] = our_tier
                    matched["updatedAt"] = now_kst.strftime("%Y-%m-%d")
                    # 코스튬 정보가 더 상세하면 갱신
                    if eng_raw.lower() != matched.get("name_en", "").lower():
                        matched["costume_en"] = eng_raw
                continue

            # 신캐 -> 새로 생성
            new_id = slugify(eng_raw)
            # id 중복 방지
            if new_id in char_by_id:
                new_id = slugify(eng_raw + "-" + tier_letter)

            if new_id in char_by_id:
                continue

            # 한글 이름이 영문 fallback이면 스킵 (번역 사전에 없는 경우)
            if ko == eng_raw.title() and eng_low not in KO_NAME:
                print(f"[BD2] 신캐 스킵 (한글 매핑 없음): {eng_raw}")
                continue

            new_char = {
                "id": new_id,
                "name": ko,  # 한글 이름 강제
                "name_en": eng_raw,
                "grade": our_tier,
                "tier": our_tier,
                "element": "Unknown",
                "attribute": "Unknown",
                "role": "Unknown",
                "type": "Standard",
                "costume": eng_raw,
                "costume_en": eng_raw,
                "pve": 9.0 if our_tier == "SS+" else 8.5 if our_tier == "SS" else 8.0,
                "pvp": 9.0 if our_tier == "SS+" else 8.5 if our_tier == "SS" else 8.0,
                "guild": 9.0,
                "boss": 9.0,
                "image": f"https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/{new_id}.png",
                "summary": f"신규 캐릭터 {ko}",
                "detail": f"{eng_raw} ({ko}) - {tier_letter}티어 신규 추가. {now_kst.strftime('%Y-%m-%d')} 자동 크롤링.",
                "gear": [],
                "team": [],
                "pros": [f"{tier_letter}티어 신규"],
                "cons": [],
                "invest": 3,
                "beginner": False,
                "updatedAt": now_kst.strftime("%Y-%m-%d")
            }
            print(f"[BD2] 신캐 추가: {ko} ({eng_raw}) -> {new_id} [{our_tier}]")
            characters.append(new_char)
            char_by_id[new_id] = new_char
            new_chars.append({"id": new_id, "name": ko, "tier": our_tier, "from_en": eng_raw})

    # 정렬: SS+ > SS > S > A > B
    def sort_key(c):
        return (-TIER_ORDER.get(c.get("tier", "B"), 0), c.get("name", ""))

    characters_sorted = sorted(characters, key=sort_key)

    with open(CHAR_PATH, "w", encoding="utf-8") as f:
        json.dump(characters_sorted, f, ensure_ascii=False, indent=2)
    print(f"[BD2] characters.json 저장: {len(characters_sorted)}개 (신규 {len(new_chars)}개)")

    iso_year, iso_week, _ = now_kst.isocalendar()
    week_of_month = (now_kst.day - 1) // 7 + 1

    new_weekly = {
        **weekly,
        "version": f"{now_kst.year}년 {now_kst.month:02d}월 {week_of_month}주차 (W{iso_week})",
        "updated": now_kst.strftime("%Y-%m-%d"),
        "updated_at": now_kst.isoformat(),
        "deployed_at": now_kst.isoformat(),
        "meta": f"자동 업데이트 - S:{len(tiers['S'])} A:{len(tiers['A'])} B:{len(tiers['B'])} C:{len(tiers['C'])} / 전체 {len(characters_sorted)}명",
        "buff": buff,
        "nerf": nerf,
        "new": new_chars,
        "note": f"{now_kst.strftime('%m/%d')} 크롤링 - 신캐 {len(new_chars)}명 추가",
        "banner": weekly.get("banner", ""),
        "headline": weekly.get("headline", weekly.get("banner", "")),
        "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "github_sha": os.environ.get("GITHUB_SHA", ""),
    }

    with open(WEEKLY_PATH, "w", encoding="utf-8") as f:
        json.dump(new_weekly, f, ensure_ascii=False, indent=2)
    print(f"[BD2] weekly 저장: {new_weekly['version']} buff={len(buff)} nerf={len(nerf)} new={len(new_chars)}")

if __name__ == "__main__":
    main()
