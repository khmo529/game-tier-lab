import json, os, re, requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

DATA_DIR = "games/nikke/data"
CHAR_FILE = os.path.join(DATA_DIR, "characters.json")
WEEKLY_FILE = os.path.join(DATA_DIR, "weekly-update.json")
RAW_FILE = os.path.join(DATA_DIR, "prydwen_raw.json")
FALLBACK_FILE = os.path.join(DATA_DIR, "fallback_2026.json")

BASE_IMAGE_URL = "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/"

EN_TO_KO = {
    "Anis: Star": "아니스: 스타",
    "Flora (Treasure)": "플로라(트레저)",
    "Ada Wong": "에이다 웡",
    "Vesti: Tactical Upgrade": "베스티: 택티컬 업그레이드",
    "Moran (Treasure)": "모란(트레저)",
    "Siren": "세이렌",
    "Mast: Romantic Maid": "마스트: 로맨틱 메이드",
    "Nayuta": "나유타",
    "Takina Inoue": "타키나 이노우에",
    "Cinderella: Crystal Wave": "신데렐라: 크리스탈 웨이브",
    "Laplace: Ultimate Hero": "라플라스: 얼티밋 히어로",
    "Privaty (Treasure)": "프리바티(트레저)",
    "Scarlet: Black Shadow": "스칼렛: 블랙 섀도우",
    "Rapi: Red Hood": "라피: 레드 후드",
    "Crown": "크라운",
    "Scarlet": "홍련",
}

TIER_ORDER = {"SSS":0,"SS":1,"S":2,"A":3,"B":4,"C":5,"D":6,"F":7}
PRYDWEN_MAP = {"SSS":"SSS","SS":"SS","S":"S","A":"A","B":"B","C":"C","D":"C","E":"C","F":"C"}

def to_image_filename(en_name: str) -> str:
    """
    영어 이름으로 이미지 경로 자동 생성
    예: "Scarlet" -> "Scarlet.jpg"
        "Scarlet: Black Shadow" -> "Scarlet_Black_Shadow.jpg"
        "Anis: Star" -> "Anis_Star.jpg"
        "Flora (Treasure)" -> "Flora_Treasure.jpg"
    """
    if not en_name:
        return ""
    # 1. 양쪽 공백 제거
    s = en_name.strip()
    # 2. 괄호 안 내용 유지하되 괄호 기호 제거
    s = s.replace("(", " ").replace(")", " ")
    # 3. 콜론, 슬래시 등은 공백으로
    s = s.replace(":", " ").replace("/", " ").replace("\\", " ")
    # 4. 특수문자 제거 (알파벳, 숫자, 공백, -, _ 만 남김)
    s = re.sub(r"[^A-Za-z0-9 _-]", "", s)
    # 5. 공백을 _ 로 통일, 중복 _ 제거
    s = "_".join(s.split())
    s = re.sub(r"_+", "_", s).strip("_")
    # 6. 빈 문자열이면 fallback
    if not s:
        s = "Unknown"
    return f"{BASE_IMAGE_URL}{s}.jpg"

def load_fallback():
    for p in [FALLBACK_FILE, "fallback_2026.json", "/mnt/data/fallback_2026.json", "/mnt/data/characters_with_short.json"]:
        if os.path.exists(p):
            try:
                with open(p,"r",encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
    return []

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
        fb=load_fallback()
        if fb:
            print(f"[INFO] fallback {len(fb)} 복구")
            chars=fb
        else:
            print("[ERROR] no fallback")
            return

    # 기존 캐릭터들 이미지 경로도 영어 이름 기준으로 재설정
    for c in chars:
        en = c.get("en_name") or EN_TO_KO.get(c["name"]) or c["name"]
        # 영어 이름이 있으면 그걸로, 없으면 한글 이름이라도 변환 시도
        if "en_name" in c and c["en_name"]:
            c["image"] = to_image_filename(c["en_name"])
        elif c["name"] in EN_TO_KO.values():
            # KO -> EN 역매핑 찾아서 이미지 생성
            rev = {v:k for k,v in EN_TO_KO.items()}
            if c["name"] in rev:
                c["image"] = to_image_filename(rev[c["name"]])
        # 이미 image가 비어있는 경우도 영어 이름으로 채움
        if not c.get("image"):
            c["image"] = to_image_filename(c.get("en_name", c["name"]))

    raw=fetch_prydwen()
    if raw:
        with open(RAW_FILE,"w",encoding="utf-8") as f: json.dump(raw,f,ensure_ascii=False,indent=2)
    else:
        if os.path.exists(RAW_FILE):
            try:
                with open(RAW_FILE,"r",encoding="utf-8") as f: raw=json.load(f)
            except: raw={}

    changed=[]; added=[]
    now=datetime.now(timezone.utc)
    kst=datetime.now().astimezone()
    date_str=kst.strftime("%Y-%m-%d")

    existing_map={}
    for c in chars:
        if 'en_name' in c:
            existing_map[c['en_name'].lower()]=c
        existing_map[c['name'].lower()]=c

    max_id=max([c['id'] for c in chars]) if chars else 0

    for en_raw, tier_raw in raw.items():
        nt=PRYDWEN_MAP.get(tier_raw.upper(), tier_raw.upper())
        if nt not in TIER_ORDER: continue
        found=existing_map.get(en_raw.lower())
        if found:
            ot=found.get('tier','B')
            # 이미지 경로 영어 이름 기준으로 항상 최신화
            found["image"] = to_image_filename(en_raw)
            if nt!=ot:
                orank=TIER_ORDER.get(ot,99); nrank=TIER_ORDER.get(nt,99)
                typ="up" if nrank<orank else "down"
                hist=found.get('history',[]); hist.append(nt); found['history']=hist[-8:]
                found['tier']=nt
                found['rating']=5 if nt in ["SSS","SS"] else 4 if nt=="S" else 3
                changed.append({"id":found['id'],"name":found['name'],"type":typ,"from":ot,"to":nt})
                print(f"[UPDATE] {found['name']} {ot}->{nt}")
        else:
            if len(en_raw)<2 or len(en_raw)>40: continue
            # 이미지 파일명은 영어 이름 그대로
            img_path = to_image_filename(en_raw)
            max_id+=1
            ko_name=EN_TO_KO.get(en_raw, en_raw)
            new_c={
                "id": max_id,
                "name": ko_name,
                "en_name": en_raw,
                "tier": nt,
                "rarity": "SSR",
                "company": "미확인",
                "weapon": "미확인",
                "element": "미확인",
                "burst": "III",
                "position": "미확인",
                "content": ["스토리"],
                "rating": 5 if nt in ["SSS","SS"] else 4,
                "scores": {"story":5,"boss":4,"pvp":3,"raid":4,"union":4},
                "pros": [f"{tier_raw} 티어 - prydwen 자동 추가"],
                "cons": ["정보 업데이트 필요"],
                "overload": ["공격력 ↑"],
                "cube": "미확인",
                "team": [ko_name],
                "priority": ["3스킬"],
                "reroll": nt in ["SSS","SS"],
                "history": [nt],
                "image": img_path
            }
            chars.append(new_c)
            existing_map[en_raw.lower()]=new_c
            existing_map[ko_name.lower()]=new_c
            added.append(new_c['name'])
            changed.append({"id":new_c['id'],"name":ko_name,"type":"new","from":"","to":nt})
            print(f"[NEW] {ko_name} ({en_raw}) -> {nt} | {img_path}")

    with open(CHAR_FILE,"w",encoding="utf-8") as f: json.dump(chars,f,ensure_ascii=False,indent=2)

    counts={"new":len(added),"up":0,"down":0,"buff":0,"nerf":0}
    for ch in changed:
        if ch['type']=='up': counts['up']+=1
        elif ch['type']=='down': counts['down']+=1

    weekly={
        "date": date_str,
        "metaVersion": f"{kst.strftime('%Y-%m')} 메타",
        "week": f"{kst.strftime('%Y년 %m월 %d일')} 기준",
        "note": f"prydwen.gg Story 티어 기준 - {len(changed)}명 변동 ({len(added)}명 신규)",
        "counts": counts,
        "changes": changed,
        "updated_at": now.isoformat(),
        "updated_at_kst": kst.strftime("%Y-%m-%d %H:%M:%S KST"),
        "source": "prydwen.gg",
        "total": len(chars)
    }
    with open(WEEKLY_FILE,"w",encoding="utf-8") as f: json.dump(weekly,f,ensure_ascii=False,indent=2)
    print(f"DONE {len(chars)} chars - image path EN based")

if __name__=="__main__":
    main()
