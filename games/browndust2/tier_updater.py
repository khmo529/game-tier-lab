#!/usr/bin/env python3
# games/browndust2/tier_updater.py - v10: 등급 카운트 버그 수정 (S:0 문제 해결)
import json, re, os, requests
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"

KST = ZoneInfo("Asia/Seoul")
now_kst = datetime.now(KST)

TIER_ORDER = {"SS+": 6, "SS": 5, "S": 4, "A": 3, "B": 2, "C": 1, "D": 0}

KNOWN_IMAGES = [
    "acolyte-elpis.png","actingarchbishopmichaela.png","admiralsylvia.png","aliceglacia.png",
    "androidqueenlecliss.png","angelica.png","angelofdestructionteresse.png","anonymoussagenartas.png",
    "anvilofcreationlayla.png","apostlekalienolivier.png","apostlemorpeah.png","beachangelteresse.png",
    "beachvacatinmorpeah.png","beachvacationeclipse.png","bikiniagentsylvia.png","bloodgluttonjustia.png",
    "brankidolhelena.png","brankmanagergray.png","celebritybunnyloen.png","combatdoctorremnunt.png",
    "darkknightlathel.png","darksaintessliberta.png","disciniplinarycommitteeglacia.png",
    "empressoftheoceanrubia.png","fiendscholarolstein.png","firegraffitianastasia.png",
    "gentlemaidanastasia.png","herbtrackerlathel.png","ironbloodmonarchwilhelmina.png",
    "littlehunterriginette.png","lonesurvivorlathel.png","mercenaryknightcarlson.png",
    "promiseofvengeancelathel.png","rodevstarliatris.png","sageofbluecloudolstein.png",
    "sharpshooterofthemistgray.png","swordqueensylvia.png","trackandfieldteamcaptainlevia.png",
    "zzzzz-1762163612pumpkingirlsonya.png",
]
MANUAL_IMAGE_MAP = {
    "olivier-apostle-kelian": "apostlekalienolivier.png",
    "gray-the-sharpshooter-of-the-mist": "sharpshooterofthemistgray.png",
    "glacia-disciplinary-committee": "disciniplinarycommitteeglacia.png",
    "lathel-lonely-survivor": "lonesurvivorlathel.png",
    "lathel-medicinal-herb-tracker": "herbtrackerlathel.png",
    "levia-track-and-field-captain": "trackandfieldteamcaptainlevia.png",
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

def normalize(s): return re.sub(r'[^a-z0-9]','',s.lower()) if s else ""
def slugify(s):
    import re
    s=s.lower(); s=re.sub(r'[^a-z0-9]+','-',s); s=re.sub(r'^-+|-+$','',s); return s or "unknown"

def find_image_file(slug, base_en, costume_en):
    if slug in MANUAL_IMAGE_MAP: return MANUAL_IMAGE_MAP[slug]
    lower_images={f.lower():f for f in KNOWN_IMAGES}
    cand=f"{slug}.png"
    if cand.lower() in lower_images: return lower_images[cand.lower()]
    cand2=f"{normalize(costume_en)}{normalize(base_en)}.png"
    if cand2.lower() in lower_images: return lower_images[cand2.lower()]
    return f"{slug}.png"

def load_json(path, default):
    if not path.exists(): return default
    try:
        if path.stat().st_size==0: return default
        with open(path,"r",encoding="utf-8") as f: return json.load(f)
    except: return default

# 기존 하드코딩 리스트 (생략 - v9와 동일, 130개)
def get_hardcoded_full_list():
    return [
        ("Alec","The Destruction"),("Alec","Sword Breaker"),("Anatasia","Gentle Maid"),("Anatasia","Fire Graffiti"),
        ("Andrew","Loyal Butler"),("Andrew","Specialist"),("Arines","Priest of Vitality"),("Bernie","Righteous Raider Girl"),
        ("Blade","Apostle"),("Blade","Young Lady"),("Carlson","The Mercenary Knight"),("Celia","The Curse"),
        ("Celia","Descendant of the Great Witch"),("Celia","Masquerade Bunny"),("Dalvi","Bright Moon"),("Dalvi","Summer Vacation"),
        ("Darian","Prophetic Dream"),("Eclipse","Dimension Witch"),("Eclipse","Nightmare Bunny"),("Eclipse","Beach Vacation"),
        ("Eclipse","Dream Bride"),("Eleaneer","Piercing Magic Bow"),("Eleaneer","B-Rank Idol"),("Elise","Lovely Lady"),
        ("Elise","Code Name O"),("Elpis","Hand of Salvation"),("Emma","Haggard Delinquent"),("Emma","School Queen"),
        ("Fred","Lugo Defense Force"),("Glacia","Alice"),("Glacia","Disciplinary Committee"),("Goblin Slayer","Orcbolg"),
        ("Granhildr","The Void"),("Granhildr","Comeback Idol"),("Granhildr","Boo Ghost"),("Gray","The Sharpshooter of the Mist"),
        ("Gray","B-Rank Manager"),("Gray","Vanguard"),("Gray","Pool Party"),("Gynt","Lugo Hunter"),("Helena","Top Idol"),
        ("Helena","B-Rank Idol"),("Hikage","Kind Ruthlessness"),("High Elf Archer","Daughter of Starwind"),("Ingrid","Kardis' Bullet"),
        ("Jayden","Beautiful Girl Devotee"),("Jayden","Manga Research Club"),("Julie","Healer"),("Justia","Knight of Blood"),
        ("Justia","White Reaper"),("Justia","Blood Glutton"),("Justia","Kendo Club"),("Justia","Pool Party"),("Justia","Hot Summer Dream"),
        ("Kry","Liberated Marauder"),("Kry","Violent Student"),("Lathel","Medicinal Herb Tracker"),("Lathel","Lonely Survivor"),
        ("Lathel","Homunculus"),("Lathel","Dark Knight"),("Lathel","Promise of Vengance"),("Lathel","Pool Party"),
        ("Layla","Anvil of Creation"),("Lecliss","Killer Doll"),("Lecliss","Android Queen"),("Levia","Track and Field Captain"),
        ("Levia","Night of Jealousy"),("Levia","Overheat"),("Liatris","Rodev's Star"),("Liatris","Maid Name R"),("Liatris","Neon Stalker"),
        ("Liberta","Dark Saintess"),("Liberta","Onsen Manager"),("Lisianne","Wandering Priest"),("Loen","Last Hope"),
        ("Loen","Track and Field Team"),("Loen","Celebrity Bunny"),("Lucrezia","Seductive Wings"),("Luvencia","Deal Snatcher"),
        ("Luvencia","Wild Dog"),("Maria","Archmage"),("Michaela","Acting Archbishop"),("Michaela","Beachside Justice"),
        ("Morpeah","Apostle"),("Morpeah","Beach Vacation"),("Morpeah","Daydream Bunny"),("Nartas","Anonymous Sage"),
        ("Nebris","Labyrinth Gatekeeper"),("Nebris","Laid-back Lifeguard"),("Nebris","New Hire"),("Olivier","Apostle (Kelian)"),
        ("Olivier","Fallen Wings"),("Olivier","White Witch"),("Olstein","The Fiend Scholar"),("Olstein","Sage of Blue Clouds"),
        ("Priestess","Earth Mother Believer"),("Rafina","Steel Engine"),("Rafina","Code Name A"),("Rafina","Game Club"),
        ("Refithea","The Gluttonous"),("Refithea","Pure White Blessing"),("Refithea","Poolside Fairy"),("Remnunt","Combat Doctor"),
        ("Rigenette","Little Hunter"),("Roxy","Respected Master"),("Roxy","Emerging Desire"),("Rou","White Cat"),("Rou","Red Hat"),
        ("Rou","Nature's Claw"),("Rou","Stray Cat"),("Rubia","Thorn of the Desert"),("Rubia","The Empress of the Ocean"),
        ("Rubia","Maid Name C"),("Rubia","Maid Bikini"),("Sacred Justia","Reclaimed Destiny"),("Samay","Kind Liberator"),
        ("Samay","Kind Student"),("Seir","Demon's Daughter"),("Seir","B-Rank Idol"),("Seir","New Hire"),("Sonya","Shadowed Dream"),
        ("Sonya","Little Pumpkin Girl"),("Sword Maiden","Supreme God Archbishop"),("Sylvia","Desert Flower"),("Sylvia","The Sword Queen"),
        ("Sylvia","Admiral"),("Sylvia","Bikini Agent"),("Teresse","Angel of Destruction"),("Teresse","Medical Club"),
        ("Teresse","Beachside Angel"),("Teresse","Milky Bikini"),("Tyr","Starlight Guardian"),("Venaka","DJ"),("Venaka","Wind Dancer"),
        ("Ventana","Snow White"),("Ventana","Comeback Idol"),("Ventana","Onsen Practitioner"),("Wilhelmina","Iron Monarch"),
        ("Wilhelmina","Water Park Queen"),("Wiggle","Bomb Fanatic"),("Wiggle","Bomb in the Hoodie"),("Yomi","Gentle Destroyer"),
        ("Yozakura","Fist of Conviction"),("Yumi","Dancing Snowflake"),("Yuri","Whitebolt"),("Yuri","Comeback Idol"),
        ("Zenith","Robin Hood"),("Zenith","Poolside Guardian"),
    ]

def main():
    existing = load_json(CHAR_PATH, [])
    print(f"[BD2] 기존 {len(existing)}개")

    # 등급 집계는 기존 캐릭터 기준
    grade_counter = Counter()
    for c in existing:
        grade_counter[c.get('grade', c.get('tier','C'))] += 1

    print(f"[BD2] 등급 분포: {dict(grade_counter)}")

    # weekly 업데이트 - 외부 크롤링 실패해도 실제 등급으로 표시
    weekly = load_json(WEEKLY_PATH, {})
    iso_week = now_kst.isocalendar()[1]
    wom = (now_kst.day-1)//7+1

    # S:0 A:0 방지: 실제 grade_counter 사용
    order = ['SS+','SS','S','A','B','C']
    meta_parts = []
    for t in order:
        if t in grade_counter:
            meta_parts.append(f"{t}:{grade_counter[t]}")

    meta_str = f"전체 {len(existing)}개 / " + " ".join(meta_parts) if meta_parts else f"전체 {len(existing)}개"

    new_weekly = {
        **weekly,
        "version": f"{now_kst.year}년 {now_kst.month:02d}월 {wom}주차 (W{iso_week})",
        "updated": now_kst.strftime("%Y-%m-%d"),
        "updated_at": now_kst.isoformat(),
        "deployed_at": now_kst.isoformat(),
        "meta": meta_str,
        "total": len(existing),
        "grades": dict(grade_counter),
        "github_run_id": os.environ.get("GITHUB_RUN_ID",""),
        "github_sha": os.environ.get("GITHUB_SHA",""),
    }
    with open(WEEKLY_PATH, "w", encoding="utf-8") as f:
        json.dump(new_weekly, f, ensure_ascii=False, indent=2)
    print(f"[BD2] weekly 수정 완료: {meta_str}")

if __name__ == "__main__":
    main()
