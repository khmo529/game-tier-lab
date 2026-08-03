#!/usr/bin/env python3
# games/browndust2/tier_updater.py - v7: 전체 캐릭터 수집 + 한글 이름 완전체
import json, re, os, requests
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

# 베이스 캐릭터 한글
BASE_KO = {
    "alec": "알렉", "anatasia": "아나타샤", "andrew": "앤드류", "arines": "아리네스",
    "bernie": "버니", "blade": "블레이드", "carlson": "칼슨", "celia": "셀리아",
    "dalvi": "달비", "darian": "다리안", "eclipse": "이클립스", "eleaneer": "엘라니어",
    "elise": "엘리스", "elpis": "엘피스", "emma": "엠마", "fred": "프레드",
    "glacia": "글라시아", "goblin slayer": "고블린 슬레이어", "granhildr": "그란힐드르",
    "gray": "그레이", "gynt": "귄트", "helena": "헬레나", "hikage": "히카게",
    "high elf archer": "하이엘프 궁수", "ingrid": "잉그리드", "jayden": "제이든",
    "julie": "줄리", "justia": "유스티아", "kry": "크라이", "lathel": "라텔",
    "layla": "라일라", "lecliss": "레클리스", "levia": "레비아", "liatris": "리아트리스",
    "liberta": "리베르타", "lisianne": "리시안", "loen": "로엔", "lucrezia": "루크레치아",
    "luvencia": "루벤시아", "maria": "마리아", "michaela": "미카엘라", "morpeah": "모르페아",
    "nartas": "나르타스", "nebris": "네브리스", "olivier": "올리비에", "olstein": "올스테인",
    "priestess": "프리스트", "rafina": "라피네", "rafine": "라피네", "refithea": "레피테아",
    "remnunt": "렘넌트", "rigenette": "리제트", "roxy": "록시", "rou": "루",
    "rubia": "루비아", "sacred justia": "성스러운 유스티아", "samay": "사메이",
    "seir": "세이르", "sonya": "소냐", "sword maiden": "검의 무녀",
    "sylvia": "실비아", "teresse": "테리스", "terisse": "테리스", "tyr": "티르",
    "venaka": "베나카", "ventana": "벤타나", "wilhelmina": "빌헬미나", "wiggle": "위글",
    "yomi": "요미", "yozakura": "요자쿠라", "yumi": "유미", "yuri": "유리",
    "zenith": "제니스", "scheherazade": "셰헤라자드", "schera": "셰헤라자드",
    "samay": "사메이", "angelica": "안젤리카", "sentana": "센타나", "luvencia": "루벤시아",
}

COSTUME_KO = {
    "the destruction": "파괴", "sword breaker": "검 파괴자", "gentle maid": "온화한 메이드",
    "fire graffiti": "불꽃 그래피티", "loyal butler": "충성스러운 집사", "specialist": "전문가",
    "priest of vitality": "활력의 사제", "righteous raider girl": "정의의 약탈 소녀",
    "apostle": "사도", "young lady": "영애", "the mercenary knight": "용병 기사",
    "the curse": "저주", "descendant of the great witch": "대마녀의 후예",
    "masquerade bunny": "가면무도회 버니", "bright moon": "명월", "summer vacation": "여름 휴가",
    "prophetic dream": "예지몽", "dimension witch": "차원 마녀", "nightmare bunny": "악몽 버니",
    "beach vacation": "해변 휴가", "dream bride": "꿈의 신부", "piercing magic bow": "관통의 마법 활",
    "b-rank idol": "B랭크 아이돌", "lovely lady": "사랑스러운 숙녀", "code name o": "코드네임 O",
    "hand of salvation": "구원의 손", "haggard delinquent": "초췌한 불량소녀", "school queen": "학교 퀸",
    "lugo defense force": "루고 방위군", "alice": "앨리스", "disciplinary committee": "풍기위원",
    "orcborg": "오르크볼그", "the void": "공허", "comeback idol": "컴백 아이돌", "boo ghost": "부끄고스트",
    "the sharpshooter of the mist": "안개의 명사수", "b-rank manager": "B랭크 매니저",
    "vanguard": "선봉", "pool party": "풀파티", "lugo hunter": "루고 헌터", "top idol": "탑 아이돌",
    "kind ruthlessness": "친절한 무자비", "daughter of starwind": "별바람의 딸",
    "kardis' bullet": "카르디스의 총알", "beautiful girl devotee": "미소녀 신봉자",
    "manga research club": "만화 연구부", "healer": "힐러", "knight of blood": "피의 기사",
    "white reaper": "백색 사신", "blood glutton": "피의 탐식자", "kendo club": "검도부",
    "hot summer dream": "한여름의 꿈", "liberated marauder": "해방된 약탈자",
    "violent student": "폭력 학생", "medicinal herb tracker": "약초 추적자",
    "lonely survivor": "고독한 생존자", "homunculus": "호문쿨루스", "dark knight": "다크 나이트",
    "promise of vengance": "복수의 맹세", "anvil of creation": "창조의 모루",
    "killer doll": "킬러 인형", "android queen": "안드로이드 여왕",
    "track and field captain": "육상부 주장", "night of jealousy": "질투의 밤",
    "overheat": "오버히트", "rodev's star": "로데브의 별", "maid name r": "메이드 R",
    "neon stalker": "네온 스토커", "dark saintess": "암흑 성녀", "onsen manager": "온천 관리자",
    "wandering priest": "방랑 사제", "last hope": "마지막 희망", "track and field team": "육상부",
    "celebrity bunny": "셀럽 버니", "seductive wings": "유혹의 날개", "deal snatcher": "거래 사냥꾼",
    "wild dog": "야생 개", "archmage": "대마법사", "acting archbishop": "대행 대주교",
    "beachside justice": "해변의 정의", "queen of signatures": "서명의 여왕",
    "beach vacation": "해변 휴가", "daydream bunny": "백일몽 버니", "anonymous sage": "익명의 현자",
    "labyrinth gatekeeper": "미궁 수문장", "laid-back lifeguard": "느긋한 인명구조원",
    "new hire": "신입", "apostle (kelian)": "사도 (켈리안)", "fallen wings": "타락한 날개",
    "white witch": "백색 마녀", "the fiend scholar": "악마 학자", "sage of blue clouds": "청운의 현자",
    "earth mother believer": "대지모 신도", "steel engine": "강철 엔진", "code name a": "코드네임 A",
    "game club": "게임부", "the gluttonous": "탐식가", "pure white blessing": "순백의 축복",
    "poolside fairy": "풀사이드 요정", "combat doctor": "전투 의사", "little hunter": "꼬마 사냥꾼",
    "respected master": "존경받는 스승", "emerging desire": "피어나는 욕망", "white cat": "하얀 고양이",
    "red hat": "빨간 모자", "nature's claw": "자연의 발톱", "stray cat": "길고양이",
    "thorn of the desert": "사막의 가시", "the empress of the ocean": "바다의 여제",
    "maid name c": "메이드 C", "maid bikini": "메이드 비키니", "reclaimed destiny": "되찾은 운명",
    "kind liberator": "친절한 해방자", "kind student": "친절한 학생", "demon's daughter": "악마의 딸",
    "shadowed dream": "그림자 꿈", "little pumpkin girl": "꼬마 호박 소녀",
    "supreme god archbishop": "지고신의 대주교", "desert flower": "사막의 꽃",
    "the sword queen": "검의 여왕", "admiral": "제독", "bikini agent": "비키니 요원",
    "angel of destruction": "파괴의 천사", "medical club": "의무부", "beachside angel": "해변의 천사",
    "milky bikini": "밀키 비키니", "starlight guardian": "별빛 수호자", "dj": "DJ",
    "wind dancer": "바람의 무희", "snow white": "백설", "onsen practitioner": "온천 수행가",
    "iron monarch": "철의 군주", "water park queen": "워터파크 여왕", "bomb fanatic": "폭탄광",
    "bomb in the hoodie": "후드 속 폭탄", "gentle destroyer": "온화한 파괴자",
    "fist of conviction": "신념의 주먹", "dancing snowflake": "춤추는 눈송이",
    "whitebolt": "화이트볼트", "robin hood": "로빈 후드", "poolside guardian": "풀사이드 가디언",
    "beachside justice michaela": "해변의 정의 미카엘라", "magical innovator diana": "마법 혁신가 디아나",
    "bikini agent sylvia": "비키니 요원 실비아", "deadeye nekyndalia": "데드아이 네킨달리아",
}

def ko_base(base_en):
    return BASE_KO.get(base_en.lower().strip(), base_en.title())

def ko_costume(cost_en):
    return COSTUME_KO.get(cost_en.lower().strip(), cost_en.title())

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
    except:
        return default

def fetch_all_characters_fandom():
    url = "https://gachagames.fandom.com/wiki/Brown_Dust_2_characters"
    headers = {"User-Agent": "Mozilla/5.0 BD2-full-bot"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        # 페이지 전체 텍스트에서 "Alec: The Destruction" 패턴 추출
        text = soup.get_text(separator=",", strip=True)
        # 정규식: 단어: 단어 형태
        # 예: "Alec: The Destruction" - 콜론 앞뒤로 공백 있을 수 있음
        pattern = r"([A-Za-z0-9' \-]+?)\s*:\s*([A-Za-z0-9' \-]+)"
        matches = re.findall(pattern, text)
        # 필터: 너무 짧거나 의미없는 것 제외, Playable characters 섹션만
        chars = []
        for base, costume in matches:
            base = base.strip()
            costume = costume.strip()
            if len(base) < 2 or len(costume) < 2:
                continue
            if base.lower() in ["playable characters", "this is a list"]:
                continue
            # 중복 방지용 full
            full = f"{base}: {costume}"
            if len(full) > 60:
                continue
            chars.append((base, costume))
        # 중복 제거
        uniq = []
        seen = set()
        for b,c in chars:
            key = f"{b.lower()}:{c.lower()}"
            if key not in seen:
                seen.add(key)
                uniq.append((b,c))
        print(f"[BD2] Fandom에서 {len(uniq)}개 캐릭터 코스튬 수집")
        return uniq
    except Exception as e:
        print(f"[BD2] Fandom 크롤 실패: {e}")
        return []

def fetch_tiers():
    url = "https://www.pockettactics.com/brown-dust-2/tier-list"
    headers = {"User-Agent": "Mozilla/5.0 BD2-tier"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        tiers = {"S": [], "A": [], "B": [], "C": []}
        pattern = r"\|\s*([SABCD])\s*\|\s*([^|]+?)\s*\|"
        matches = re.findall(pattern, r.text, re.IGNORECASE)
        for letter, names_blob in matches:
            letter = letter.upper()
            if letter not in tiers:
                continue
            names = [n.strip() for n in names_blob.split(",") if n.strip()]
            tiers[letter].extend(names)
        print(f"[BD2] Tier: S={len(tiers['S'])} A={len(tiers['A'])} B={len(tiers['B'])} C={len(tiers['C'])}")
        return tiers
    except Exception as e:
        print(f"[BD2] Tier fetch fail: {e}")
        return {"S":[], "A":[], "B":[], "C":[]}

def tier_of_character(base, costume, tiers):
    full1 = f"{base}: {costume}".lower()
    full2 = f"{base} {costume}".lower()
    base_low = base.lower()
    costume_low = costume.lower()
    # 정확히 일치 검색
    for letter, names in tiers.items():
        for n in names:
            nl = n.lower()
            if nl in full1 or full1 in nl or nl == base_low or nl == costume_low or base_low in nl:
                return letter
    return None

def main():
    existing = load_json(CHAR_PATH, [])
    print(f"[BD2] 기존 {len(existing)}개")
    existing_by_slug = {c["id"]: c for c in existing}

    all_fandom = fetch_all_characters_fandom()
    tiers = fetch_tiers()

    tier_map = {"S": "SS+", "A": "SS", "B": "S", "C": "A", "D": "B"}

    new_characters = []
    # 기존 유지 + 신규 병합
    for base_en, costume_en in all_fandom:
        base_ko = ko_base(base_en)
        costume_ko = ko_costume(costume_en)
        # 한글 이름: "베이스 (코스튬)" 형태
        # 코스튬이 베이스와 같으면 베이스만
        if base_ko.lower() == costume_ko.lower():
            name_ko = base_ko
        else:
            name_ko = f"{base_ko} ({costume_ko})"

        slug = slugify(f"{base_en}-{costume_en}")
        tier_letter = tier_of_character(base_en, costume_en, tiers)
        our_tier = tier_map.get(tier_letter, "B") if tier_letter else "B"

        # 기존에 있으면 티어만 업데이트
        if slug in existing_by_slug:
            c = existing_by_slug[slug]
            # 한글 이름 강제 업데이트
            if c.get("name") != name_ko:
                print(f"[BD2] 한글명 갱신: {c.get('name')} -> {name_ko}")
                c["name"] = name_ko
            if tier_letter:
                c["tier"] = our_tier
                c["grade"] = our_tier
            c["updatedAt"] = now_kst.strftime("%Y-%m-%d")
            new_characters.append(c)
        else:
            # 신규 생성
            char = {
                "id": slug,
                "name": name_ko,
                "name_en": f"{base_en}: {costume_en}",
                "base_en": base_en,
                "base_ko": base_ko,
                "costume": costume_en,
                "costume_ko": costume_ko,
                "grade": our_tier,
                "tier": our_tier,
                "tier_source": tier_letter or "unranked",
                "element": "Unknown",
                "attribute": "Unknown",
                "role": "Unknown",
                "type": "Costume",
                "pve": 9.5 if our_tier == "SS+" else 8.8 if our_tier == "SS" else 8.0,
                "pvp": 9.5 if our_tier == "SS+" else 8.8 if our_tier == "SS" else 8.0,
                "guild": 8.5,
                "boss": 8.5,
                "image": f"https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/{slug}.png",
                "summary": f"{name_ko} - {our_tier}티어",
                "detail": f"{base_en}의 {costume_en} 코스튬. {name_ko}는 {our_tier}티어로 평가됩니다.",
                "gear": [],
                "team": [],
                "pros": [f"{tier_letter or 'Unranked'}티어" if tier_letter else "신규"],
                "cons": [],
                "invest": 3,
                "beginner": False,
                "updatedAt": now_kst.strftime("%Y-%m-%d")
            }
            new_characters.append(char)

    # 기존에 있었는데 fandom에 없는 캐릭터도 유지 (18개 원본)
    for c in existing:
        if c["id"] not in [x["id"] for x in new_characters]:
            # 한글 이름 보정
            base = c.get("base_en") or c.get("id")
            if "name" in c and any(ord('a') <= ord(ch.lower()) <= ord('z') for ch in c["name"]):
                # 영문이 포함되어 있으면 한글로 교체 시도
                maybe_ko = BASE_KO.get(base.lower() if base else "", None)
                if maybe_ko:
                    c["name"] = maybe_ko
            new_characters.append(c)

    # 정렬
    def sort_key(c):
        return (-{"SS+":6,"SS":5,"S":4,"A":3,"B":2,"C":1,"D":0}.get(c.get("tier","B"),0), c.get("name",""))

    new_characters_sorted = sorted(new_characters, key=sort_key)

    with open(CHAR_PATH, "w", encoding="utf-8") as f:
        json.dump(new_characters_sorted, f, ensure_ascii=False, indent=2)
    print(f"[BD2] 전체 저장: {len(new_characters_sorted)}개")

    iso_week = now_kst.isocalendar()[1]
    week_of_month = (now_kst.day - 1)//7 + 1
    weekly = load_json(WEEKLY_PATH, {})
    new_weekly = {
        **weekly,
        "version": f"{now_kst.year}년 {now_kst.month:02d}월 {week_of_month}주차 (W{iso_week})",
        "updated": now_kst.strftime("%Y-%m-%d"),
        "updated_at": now_kst.isoformat(),
        "deployed_at": now_kst.isoformat(),
        "meta": f"전체 {len(new_characters_sorted)}개 캐릭터 / S:{len(tiers['S'])} A:{len(tiers['A'])} B:{len(tiers['B'])} C:{len(tiers['C'])}",
        "total": len(new_characters_sorted),
        "github_run_id": os.environ.get("GITHUB_RUN_ID",""),
        "github_sha": os.environ.get("GITHUB_SHA",""),
    }
    with open(WEEKLY_PATH, "w", encoding="utf-8") as f:
        json.dump(new_weekly, f, ensure_ascii=False, indent=2)
    print(f"[BD2] weekly 저장: {new_weekly['version']}")

if __name__ == "__main__":
    main()
