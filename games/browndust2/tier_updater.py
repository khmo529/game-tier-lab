#!/usr/bin/env python3
# games/browndust2/tier_updater.py - v9: 167개 유지 + 실제 217개 이미지 파일 매칭 + 한글 강제
import json, re, os, requests
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"

KST = ZoneInfo("Asia/Seoul")
now_kst = datetime.now(KST)

TIER_ORDER = {"SS+": 6, "SS": 5, "S": 4, "A": 3, "B": 2, "C": 1, "D": 0}

# ===== 실제 서버에 존재하는 217개 파일 리스트 (list_all_images.php 결과) =====
KNOWN_IMAGES = [
    "17682970-1760522855.png","acolyte-elpis.png","actingarchbishopmichaela.png","admiralsylvia.png",
    "adventureroftheunknowndiana.png","aliceglacia.png","alignment-icon.png","androidqueenlecliss.png",
    "angelica.png","angelofdestructionteresse.png","anonymoussagenartas.png","antidystopiadiana.png",
    "anvilofcreationlayla.png","apostleblade.png","apostlekalienolivier.png","apostlemorpeah.png",
    "apprenticespearmanlydia.png","archmage-olstein.png","archmagemaria.png","beachangelteresse.png",
    "beachsidejusticemichaela.png","beachvacatinmorpeah.png","beachvacationeclipse.png",
    "bikiniagentsylvia.png","blade-dancer-justia.png","bloodgluttonjustia.png","bombfanaticwiggle.png",
    "bombinthehoodiewiggle.png","brankidoleleaneer.png","brankidolhelena.png","brankidolseir.png",
    "brankmanagergray.png","brightmoondalvi.png","celebritybunnyloen.png","code-name-s-scheherazade.png",
    "codenamearafina.png","codenameoelise.png","codenamesscheherazade.png","combatdoctorremnunt.png",
    "comebackidolgranhildr.png","comebackidolventana.png","comebackidolyuri.png","darkknightlathel.png",
    "darksaintessliberta.png","daydreambunnymorpeah.png","dealsnatcherluvencia.png","demonsdaughterseir.png",
    "descendantofthegreatwitchcelia.png","desert-sword-sylvia.png","desertflowersylvia.png",
    "dimensionalwitcheclipse.png","disciniplinarycommitteeglacia.png","djvenaka.png","dreambrideeclipse.png",
    "eclipse.png","empressoftheoceanrubia.png","executioner-alec.png","fallen-angel-angelica.png",
    "fallenwingsolivier.png","fiendscholarolstein.png","firegraffitianastasia.png","gameclubrafina.png",
    "gentlemaidanastasia.png","handofsalvationelpis.png","healerjulie.png","herbtrackerlathel.png",
    "holy-order-celia.png","homunculus-lathel.png","homunculuslathel.png","ironbloodmonarchwilhelmina.png",
    "justia.png","kendoclubjustia.png","killerdolllecliss.png","kindliberatorsamay.png","kindstudentsamay.png",
    "knightofbloodjustia.png","labyrinthgatekeepernebris.png","laidbacklifeguardnebris.png",
    "lapiswitchscheherazade.png","lasthopeloen.png","liberatedmarauderkry.png","littlehunterriginette.png",
    "lonesurvivorlathel.png","lovelyladyelise.png","loyalbutlerandrew.png","lugodefenseforcefred.png",
    "lugohuntergynt.png","magicschoolprofessorscheherazade.png","maidbikinirubia.png","maidnamecrubia.png",
    "maidnamerliatris.png","mangaresearchclubjayden.png","masqueradebunnycelia.png",
    "medical-staff-terisse.png","medicalclubteresse.png","mercenaryknightcarlson.png",
    "midsummerdreamppjustia.png","naturesclawrou.png","neonsaviorangelica.png","neonstalkerliatris.png",
    "newhirenebris.png","newhireseir.png","night-veil-seir.png","nightmarebunnyeclipse.png",
    "onsenmanagerliberta.png","onsenpractitionerventana.png","overheatlevia.png","poolpartyangelica.png",
    "poolpartygray.png","poolpartyjustia.png","poolpartylathel.png","poolpartyscheherazade.png",
    "poolsidefairyrefithea.png","poolsideguardianzenith.png","priestofvitalityarines.png",
    "promiseofvengeancelathel.png","propheticdreamdarian.png","purewhitebriderefithea.png",
    "queenofsignaturesmichaela.png","reclaimeddestinysacredjustia.png","red-hood-rou.png",
    "redridinghoodrou.png","rodevstarliatris.png","sageofbluecloudolstein.png","schoolqueenemma.png",
    "seductive-nun-lucrezia.png","seductivewingslucrezia.png","shadoweddreamsonya.png",
    "sharpshooterofthemistgray.png","starlightguardiantyr.png","steelenginerafina.png","straycatrou.png",
    "summer-eclipse-eclipse.png","summervacationdalvi.png","swordbreakeralec.png","swordqueensylvia.png",
    "tbdbaseolivier.png","thecursedcelia.png","thedestructionalec.png","thefallenangelica.png",
    "tide-prayer-rafine.png","topidolhelena.png","trackandfieldteamcaptainlevia.png",
    "trackandfieldteamloen.png","unknown-pink-diana.png","vanguardgray.png","violentstudentkry.png",
    "wanderingpriestlisianne.png","waterparkqueenwilhelmina.png","whiteboltyuri.png","whitecatrou.png",
    "whitereaperjustia.png","wilddogluvencia.png","winddancervenaka.png","youngladyblade.png",
    "zzzzz-1762163612booghostgranhildr.png","zzzzz-1762163612pumpkingirlsonya.png",
]

# 오타/축약 수동 매핑 (서버에 실제로 존재하는 파일명과 다른 경우)
MANUAL_IMAGE_MAP = {
    "olivier-apostle-kelian": "apostlekalienolivier.png",
    "gray-the-sharpshooter-of-the-mist": "sharpshooterofthemistgray.png",
    "glacia-disciplinary-committee": "disciniplinarycommitteeglacia.png",
    "lathel-lonely-survivor": "lonesurvivorlathel.png",
    "lathel-medicinal-herb-tracker": "herbtrackerlathel.png",
    "levia-track-and-field-captain": "trackandfieldteamcaptainlevia.png",
    "refithea-pure-white-blessing": "purewhitebriderefithea.png",
    "rou-red-hat": "redridinghoodrou.png",
    "rubia-the-empress-of-the-ocean": "empressoftheoceanrubia.png",
    "liatris-rodev-s-star": "rodevstarliatris.png",
    "rigenette-little-hunter": "littlehunterriginette.png",
    "morpeah-beach-vacation": "beachvacatinmorpeah.png",
    "wilhelmina-iron-monarch": "ironbloodmonarchwilhelmina.png",
    "sonya-little-pumpkin-girl": "zzzzz-1762163612pumpkingirlsonya.png",
    "sylvia-the-sword-queen": "swordqueensylvia.png",
    "anatasia-fire-graffiti": "firegraffitianastasia.png",
    "anatasia-gentle-maid": "gentlemaidanastasia.png",
    "olstein-the-fiend-scholar": "fiendscholarolstein.png",
    "olstein-sage-of-blue-clouds": "sageofbluecloudolstein.png",
    "carlson-the-mercenary-knight": "mercenaryknightcarlson.png",
    "teresse-beachside-angel": "beachangelteresse.png",
}

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
    "priestess": "대지모 신도", "rafina": "라피네", "refithea": "레피테아",
    "remnunt": "렘넌트", "rigenette": "리제트", "roxy": "록시", "rou": "루",
    "rubia": "루비아", "sacred justia": "성스러운 유스티아", "samay": "사메이",
    "seir": "세이르", "sonya": "소냐", "sword maiden": "검의 무녀",
    "sylvia": "실비아", "teresse": "테리스", "tyr": "티르",
    "venaka": "베나카", "ventana": "벤타나", "wilhelmina": "빌헬미나", "wiggle": "위글",
    "yomi": "요미", "yozakura": "요자쿠라", "yumi": "유미", "yuri": "유리",
    "zenith": "제니스", "scheherazade": "셰헤라자드", "schera": "셰헤라자드",
    "angelica": "안젤리카", "queen of signatures": "서명의 여왕", "diana": "다이아나",
    "rafine": "라피네",
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
    "orcborg": "오크볼그", "the void": "공허", "comeback idol": "컴백 아이돌", "boo ghost": "부끄고스트",
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
    "beachside justice": "해변의 정의", "daydream bunny": "백일몽 버니", "anonymous sage": "익명의 현자",
    "labyrinth gatekeeper": "미궁 수문장", "laid-back lifeguard": "느긋한 인명구조원",
    "new hire": "신입", "apostle (kelian)": "사도 켈리안", "fallen wings": "타락한 날개",
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
    "summer eclipse": "서머 이클립스", "unknown pink": "언노운 핑크", "holy order": "홀리 오더",
    "tide prayer": "타이드 프레어",
}

def ko_base(b): return BASE_KO.get(b.lower().strip(), b.title())
def ko_costume(c): return COSTUME_KO.get(c.lower().strip(), c.title())
def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s or "unknown"

def normalize(s):
    return re.sub(r'[^a-z0-9]', '', s.lower()) if s else ""

def find_image_file(slug, base_en, costume_en):
    # 1. 수동 매핑 우선
    if slug in MANUAL_IMAGE_MAP:
        fname = MANUAL_IMAGE_MAP[slug]
        if fname.lower() in [f.lower() for f in KNOWN_IMAGES]:
            return fname
    
    # 2. 정확한 slug.png
    candidates = [
        f"{slug}.png",
        f"{normalize(costume_en)}{normalize(base_en)}.png",
        f"{normalize(costume_en)}{normalize(slug)}.png",
        f"{normalize(base_en)}.png",
        f"{normalize(costume_en)}-{normalize(base_en)}.png",
    ]
    
    lower_images = {f.lower(): f for f in KNOWN_IMAGES}
    for cand in candidates:
        if cand.lower() in lower_images:
            return lower_images[cand.lower()]
    
    # 3. 부분 일치
    search = normalize(base_en)
    for f in KNOWN_IMAGES:
        if search and search in normalize(f):
            # costume도 포함되면 더 좋음
            if normalize(costume_en) and normalize(costume_en) in normalize(f):
                return f
    for f in KNOWN_IMAGES:
        if search and search in normalize(f):
            return f
            
    # 4. fallback
    return f"{slug}.png"

def load_json(path, default):
    if not path.exists(): return default
    try:
        if path.stat().st_size == 0: return default
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except: return default

def get_hardcoded_full_list():
    raw = [
        ("Alec","The Destruction"), ("Alec","Sword Breaker"),
        ("Anatasia","Gentle Maid"), ("Anatasia","Fire Graffiti"),
        ("Andrew","Loyal Butler"), ("Andrew","Specialist"),
        ("Arines","Priest of Vitality"), ("Bernie","Righteous Raider Girl"),
        ("Blade","Apostle"), ("Blade","Young Lady"), ("Carlson","The Mercenary Knight"),
        ("Celia","The Curse"), ("Celia","Descendant of the Great Witch"), ("Celia","Masquerade Bunny"),
        ("Dalvi","Bright Moon"), ("Dalvi","Summer Vacation"), ("Darian","Prophetic Dream"),
        ("Eclipse","Dimension Witch"), ("Eclipse","Nightmare Bunny"), ("Eclipse","Beach Vacation"), ("Eclipse","Dream Bride"),
        ("Eleaneer","Piercing Magic Bow"), ("Eleaneer","B-Rank Idol"),
        ("Elise","Lovely Lady"), ("Elise","Code Name O"), ("Elpis","Hand of Salvation"),
        ("Emma","Haggard Delinquent"), ("Emma","School Queen"), ("Fred","Lugo Defense Force"),
        ("Glacia","Alice"), ("Glacia","Disciplinary Committee"), ("Goblin Slayer","Orcbolg"),
        ("Granhildr","The Void"), ("Granhildr","Comeback Idol"), ("Granhildr","Boo Ghost"),
        ("Gray","The Sharpshooter of the Mist"), ("Gray","B-Rank Manager"), ("Gray","Vanguard"), ("Gray","Pool Party"),
        ("Gynt","Lugo Hunter"), ("Helena","Top Idol"), ("Helena","B-Rank Idol"), ("Hikage","Kind Ruthlessness"),
        ("High Elf Archer","Daughter of Starwind"), ("Ingrid","Kardis' Bullet"),
        ("Jayden","Beautiful Girl Devotee"), ("Jayden","Manga Research Club"), ("Julie","Healer"),
        ("Justia","Knight of Blood"), ("Justia","White Reaper"), ("Justia","Blood Glutton"), ("Justia","Kendo Club"), ("Justia","Pool Party"), ("Justia","Hot Summer Dream"),
        ("Kry","Liberated Marauder"), ("Kry","Violent Student"),
        ("Lathel","Medicinal Herb Tracker"), ("Lathel","Lonely Survivor"), ("Lathel","Homunculus"), ("Lathel","Dark Knight"), ("Lathel","Promise of Vengance"), ("Lathel","Pool Party"),
        ("Layla","Anvil of Creation"), ("Lecliss","Killer Doll"), ("Lecliss","Android Queen"),
        ("Levia","Track and Field Captain"), ("Levia","Night of Jealousy"), ("Levia","Overheat"),
        ("Liatris","Rodev's Star"), ("Liatris","Maid Name R"), ("Liatris","Neon Stalker"),
        ("Liberta","Dark Saintess"), ("Liberta","Onsen Manager"), ("Lisianne","Wandering Priest"),
        ("Loen","Last Hope"), ("Loen","Track and Field Team"), ("Loen","Celebrity Bunny"),
        ("Lucrezia","Seductive Wings"), ("Luvencia","Deal Snatcher"), ("Luvencia","Wild Dog"),
        ("Maria","Archmage"), ("Michaela","Acting Archbishop"), ("Michaela","Beachside Justice"),
        ("Queen of Signatures","Queen of Signatures"), ("Morpeah","Apostle"), ("Morpeah","Beach Vacation"), ("Morpeah","Daydream Bunny"),
        ("Nartas","Anonymous Sage"), ("Nebris","Labyrinth Gatekeeper"), ("Nebris","Laid-back Lifeguard"), ("Nebris","New Hire"),
        ("Olivier","Apostle (Kelian)"), ("Olivier","Fallen Wings"), ("Olivier","White Witch"),
        ("Olstein","The Fiend Scholar"), ("Olstein","Sage of Blue Clouds"),
        ("Priestess","Earth Mother Believer"),
        ("Rafina","Steel Engine"), ("Rafina","Code Name A"), ("Rafina","Game Club"),
        ("Refithea","The Gluttonous"), ("Refithea","Pure White Blessing"), ("Refithea","Poolside Fairy"),
        ("Remnunt","Combat Doctor"), ("Rigenette","Little Hunter"),
        ("Roxy","Respected Master"), ("Roxy","Emerging Desire"),
        ("Rou","White Cat"), ("Rou","Red Hat"), ("Rou","Nature's Claw"), ("Rou","Stray Cat"),
        ("Rubia","Thorn of the Desert"), ("Rubia","The Empress of the Ocean"), ("Rubia","Maid Name C"), ("Rubia","Maid Bikini"),
        ("Sacred Justia","Reclaimed Destiny"), ("Samay","Kind Liberator"), ("Samay","Kind Student"),
        ("Seir","Demon's Daughter"), ("Seir","B-Rank Idol"), ("Seir","New Hire"),
        ("Sonya","Shadowed Dream"), ("Sonya","Little Pumpkin Girl"), ("Sword Maiden","Supreme God Archbishop"),
        ("Sylvia","Desert Flower"), ("Sylvia","The Sword Queen"), ("Sylvia","Admiral"), ("Sylvia","Bikini Agent"),
        ("Teresse","Angel of Destruction"), ("Teresse","Medical Club"), ("Teresse","Beachside Angel"), ("Teresse","Milky Bikini"),
        ("Tyr","Starlight Guardian"), ("Venaka","DJ"), ("Venaka","Wind Dancer"),
        ("Ventana","Snow White"), ("Ventana","Comeback Idol"), ("Ventana","Onsen Practitioner"),
        ("Wilhelmina","Iron Monarch"), ("Wilhelmina","Water Park Queen"),
        ("Wiggle","Bomb Fanatic"), ("Wiggle","Bomb in the Hoodie"),
        ("Yomi","Gentle Destroyer"), ("Yozakura","Fist of Conviction"), ("Yumi","Dancing Snowflake"),
        ("Yuri","Whitebolt"), ("Yuri","Comeback Idol"), ("Zenith","Robin Hood"), ("Zenith","Poolside Guardian"),
        # 추가: 기존 167개 유지용
        ("Diana","Unknown Pink"), ("Eclipse","Summer Eclipse"), ("Celia","Holy Order"), ("Rafine","Tide Prayer"),
    ]
    return raw

def fetch_tiers():
    url = "https://www.pockettactics.com/brown-dust-2/tier-list"
    try:
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
        r.raise_for_status()
        tiers = {"S":[], "A":[], "B":[], "C":[]}
        matches = re.findall(r"\|\s*([SABCD])\s*\|\s*([^|]+?)\s*\|", r.text, re.IGNORECASE)
        for letter, blob in matches:
            letter = letter.upper()
            if letter in tiers:
                tiers[letter].extend([n.strip() for n in blob.split(",") if n.strip()])
        print(f"[BD2] Tier fetch: S={len(tiers['S'])} A={len(tiers['A'])} B={len(tiers['B'])} C={len(tiers['C'])}")
        return tiers
    except Exception as e:
        print(f"[BD2] Tier fail: {e}")
        return {"S":[], "A":[], "B":[], "C":[]}

def main():
    existing = load_json(CHAR_PATH, [])
    existing_by_id = {c["id"]: c for c in existing}
    print(f"[BD2] 기존 {len(existing)}개")

    full_list = get_hardcoded_full_list()
    tiers = fetch_tiers()
    tier_map = {"S":"SS+", "A":"SS", "B":"S", "C":"A"}

    def find_tier(base, costume):
        low_full = f"{base} {costume}".lower()
        base_low = base.lower()
        for letter, names in tiers.items():
            for n in names:
                nl = n.lower()
                if base_low in nl or nl in low_full or nl in f"{base}: {costume}".lower():
                    return letter
        return None

    all_chars = []
    for base_en, costume_en in full_list:
        base_ko = ko_base(base_en)
        costume_ko = ko_costume(costume_en)
        name_ko = f"{base_ko} ({costume_ko})" if base_ko != costume_ko else base_ko
        slug = slugify(f"{base_en}-{costume_en}")

        tier_letter = find_tier(base_en, costume_en)
        our_tier = tier_map.get(tier_letter, "A" if "B-Rank" in costume_en or "B Rank" in costume_en else "S" if "Apostle" in costume_en else "B")

        image_file = find_image_file(slug, base_en, costume_en)
        image_url = f"https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/{image_file}"

        if slug in existing_by_id:
            c = existing_by_id[slug]
            c["name"] = name_ko
            c["tier"] = our_tier
            c["grade"] = our_tier
            c["updatedAt"] = now_kst.strftime("%Y-%m-%d")
            # 이미지는 기존 것 유지하되, 실제 파일이 존재하지 않으면 새 것으로 교체
            existing_img = c.get("image","")
            existing_base = existing_img.split("/")[-1].lower() if existing_img else ""
            if existing_base not in [f.lower() for f in KNOWN_IMAGES]:
                c["image"] = image_url
            all_chars.append(c)
        else:
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
                "element": "Unknown",
                "attribute": "Unknown",
                "role": "Unknown",
                "type": "Costume",
                "pve": 9.5 if our_tier=="SS+" else 8.8 if our_tier=="SS" else 8.0,
                "pvp": 9.5 if our_tier=="SS+" else 8.8 if our_tier=="SS" else 8.0,
                "guild": 8.5,
                "boss": 8.5,
                "image": image_url,
                "summary": f"{name_ko} - {our_tier}티어",
                "detail": f"{base_en}의 {costume_en} 코스튬. {name_ko}",
                "gear": [], "team": [], "pros": [], "cons": [], "invest": 3, "beginner": False,
                "updatedAt": now_kst.strftime("%Y-%m-%d")
            }
            all_chars.append(char)

    for c in existing:
        if c["id"] not in [x["id"] for x in all_chars]:
            all_chars.append(c)

    def sort_key(c):
        return (-TIER_ORDER.get(c.get("tier","B"),0), c.get("name",""))
    all_sorted = sorted(all_chars, key=sort_key)

    with open(CHAR_PATH, "w", encoding="utf-8") as f:
        json.dump(all_sorted, f, ensure_ascii=False, indent=2)
    print(f"[BD2] 저장 완료: {len(all_sorted)}개")

    weekly = load_json(WEEKLY_PATH, {})
    iso_week = now_kst.isocalendar()[1]
    wom = (now_kst.day-1)//7+1
    new_weekly = {
        **weekly,
        "version": f"{now_kst.year}년 {now_kst.month:02d}월 {wom}주차 (W{iso_week})",
        "updated": now_kst.strftime("%Y-%m-%d"),
        "updated_at": now_kst.isoformat(),
        "deployed_at": now_kst.isoformat(),
        "meta": f"전체 {len(all_sorted)}개 / S:{len(tiers['S'])} A:{len(tiers['A'])} B:{len(tiers['B'])} C:{len(tiers['C'])}",
        "total": len(all_sorted),
        "github_run_id": os.environ.get("GITHUB_RUN_ID",""),
        "github_sha": os.environ.get("GITHUB_SHA",""),
    }
    with open(WEEKLY_PATH, "w", encoding="utf-8") as f:
        json.dump(new_weekly, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
