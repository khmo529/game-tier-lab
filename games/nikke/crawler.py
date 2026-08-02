"""
prydwen.gg -> characters.json + weekly-update.json (script.js 호환)
- prydwen에서 티어 가져와서 characters.json 병합
- weekly-update.json은 기존 script.js가 기대하는 구조로 생성
"""
import json, os, re, requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

DATA_DIR = "games/nikke/data"
CHAR_FILE = os.path.join(DATA_DIR, "characters.json")
WEEKLY_FILE = os.path.join(DATA_DIR, "weekly-update.json")
RAW_FILE = os.path.join(DATA_DIR, "prydwen_raw.json")

EN_TO_KO = {
    "Scarlet": "홍련",
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
}
KO_TO_EN = {v:k for k,v in EN_TO_KO.items()}

TIER_ORDER = {"SSS":0, "SS":1, "S":2, "A":3, "B":4, "C":5, "D":6, "F":7}
PRYDWEN_TIER_MAP = {"SSS":"SSS","SS":"SS","S":"S","A":"A","B":"B","C":"C","D":"C","E":"C","F":"C"}

def fetch_prydwen_tiers():
    url = "https://www.prydwen.gg/nikke/tier-list"
    headers = {"User-Agent":"Mozilla/5.0","Accept-Language":"en-US,en;q=0.9,ko;q=0.8"}
    print(f"[INFO] Fetching {url}")
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    html = resp.text
    try:
        soup = BeautifulSoup(html, "lxml")
        tag = soup.find("script", id="__NEXT_DATA__")
        if tag and tag.string:
            import json as js
            data = js.loads(tag.string)
            tiers={}
            def recurse(o):
                if isinstance(o, dict):
                    if "name" in o and ("tier" in o or "rating" in o):
                        n=o.get("name"); t=o.get("tier") or o.get("rating")
                        if n and t: tiers[n]=str(t).strip().upper()
                    for v in o.values(): recurse(v)
                elif isinstance(o, list):
                    for i in o: recurse(i)
            recurse(data)
            if tiers:
                print(f"[INFO] NEXT_DATA {len(tiers)} found")
                return tiers
    except Exception as e:
        print(f"[WARN] NEXT_DATA fail {e}")
    return {}

def load_chars():
    if os.path.exists(CHAR_FILE):
        try:
            with open(CHAR_FILE,"r",encoding="utf-8") as f:
                d=json.load(f)
                if isinstance(d,list) and len(d)>=5:
                    print(f"[INFO] loaded {len(d)} chars")
                    return d
                else:
                    print(f"[WARN] chars too small ({len(d)}), will restore fallback")
        except Exception as e:
            print(f"[WARN] load fail {e}")
    return None

# Fallback 20개 (네 원본)
FALLBACK = [
  {"id":1,"name":"도로시","tier":"SSS","rarity":"SSR","company":"필그림","element":"풍압","weapon":"AR","burst":"2","position":"서포터","rating":5,"history":["SSS","SSS","SSS"],"image":"https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Dorothy.jpg","pros":["쿨감 최상"],"cons":["몸약"],"overload":["탄약","명중"],"cube":"바스티온","team":["크라운/도로시/모더니아"],"priority":["버스트>스킬1>스킬2"],"reroll":True,"scores":{"story":10,"boss":10,"pvp":8,"raid":10,"union":9}},
  {"id":2,"name":"크라운","tier":"SSS","rarity":"SSR","company":"필그림","element":"철갑","weapon":"AR","burst":"2","position":"서포터","rating":5,"history":["SSS","SSS","SS"],"image":"https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Crown.jpg","pros":["무적기"],"cons":["쿨타임"],"overload":["방어"],"cube":"바스티온","team":["크라운/도로시/홍련"],"priority":["버스트>스킬2"],"reroll":True,"scores":{"story":10,"boss":10,"pvp":9,"raid":10,"union":10}},
  {"id":3,"name":"홍련","tier":"SSS","rarity":"SSR","company":"필그림","element":"풍압","weapon":"AR","burst":"3","position":"공격","rating":5,"history":["SSS","SSS","SSS"],"image":"https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Scarlet.jpg","pros":["광역딜 최강"],"cons":["생존기 없음"],"overload":["공격","치명타"],"cube":"윙맨","team":["리터/크라운/홍련"],"priority":["스킬2>버스트"],"reroll":True,"scores":{"story":10,"boss":9,"pvp":7,"raid":10,"union":10}},
  {"id":12,"name":"스칼렛","tier":"SS","rarity":"SSR","company":"필그림","element":"풍압","weapon":"AR","burst":"3","position":"공격","rating":5,"history":["S","SS"],"image":"https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/Scarlet_Black_Shadow.jpg","pros":["강력"],"cons":["조건부"],"overload":["공격"],"cube":"윙맨","team":["리터/크라운/스칼렛"],"priority":["스킬2>버스트"],"reroll":True,"scores":{"story":9,"boss":9,"pvp":8,"raid":9,"union":9}},
]

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    chars = load_chars()
    if not chars:
        print("[INFO] fallback 복구")
        chars = FALLBACK
        # 혹시 전체 20개 필요하면 characters_full.json에서 로드 시도
        full_path = "/mnt/data/characters_full.json"
        if os.path.exists(full_path):
            try:
                with open(full_path,"r",encoding="utf-8") as f:
                    chars = json.load(f)
                    print(f"[INFO] full json {len(chars)} 로드")
            except: pass

    raw = {}
    try:
        raw = fetch_prydwen_tiers()
        with open(RAW_FILE,"w",encoding="utf-8") as f: json.dump(raw,f,ensure_ascii=False,indent=2)
    except Exception as e:
        print(f"[ERROR] prydwen fail {e}")
        if os.path.exists(RAW_FILE):
            with open(RAW_FILE,"r",encoding="utf-8") as f: raw=json.load(f)

    changed_for_weekly=[]
    now = datetime.now(timezone.utc)
    kst = datetime.now().astimezone()
    date_str = kst.strftime("%Y-%m-%d")

    for c in chars:
        ko=c.get("name"); en=c.get("en_name") or KO_TO_EN.get(ko) or ko
        new_raw = raw.get(en) or raw.get(ko)
        if not new_raw:
            for k,v in raw.items():
                if k.lower()==en.lower() or k.lower()==ko.lower():
                    new_raw=v; break
        if new_raw:
            new_tier = PRYDWEN_TIER_MAP.get(str(new_raw).upper(), str(new_raw).upper())
            old_tier = c.get("tier","B")
            if new_tier != old_tier:
                # up/down 판정
                old_rank = TIER_ORDER.get(old_tier, 99)
                new_rank = TIER_ORDER.get(new_tier, 99)
                type_ = "up" if new_rank < old_rank else "down"
                hist = c.get("history",[])
                hist.append(new_tier)
                if len(hist)>8: hist=hist[-8:]
                c["history"]=hist
                c["tier"]=new_tier
                c["rating"]=5 if new_tier in ["SSS","SS"] else 4 if new_tier=="S" else 3
                changed_for_weekly.append({
                    "id": c.get("id"),
                    "name": ko,
                    "type": type_,
                    "from": old_tier,
                    "to": new_tier
                })
                print(f"[UPDATE] {ko} {old_tier}->{new_tier} ({type_})")

    # characters.json 저장
    with open(CHAR_FILE,"w",encoding="utf-8") as f: json.dump(chars,f,ensure_ascii=False,indent=2)

    # weekly-update.json - script.js 호환 포맷으로 생성
    counts = {"new":0,"up":0,"down":0,"buff":0,"nerf":0}
    for ch in changed_for_weekly:
        if ch["type"] in counts: counts[ch["type"]]+=1

    weekly = {
        "date": date_str,
        "metaVersion": f"{kst.strftime('%Y-%m')} 메타",
        "week": f"{kst.strftime('%Y년 %m월 %d일')} 기준",
        "note": f"prydwen.gg 기준 자동 업데이트 - {len(changed_for_weekly)}명 변동",
        "counts": counts,
        "changes": changed_for_weekly,
        "updated_at": now.isoformat(),
        "updated_at_kst": kst.strftime("%Y-%m-%d %H:%M:%S KST"),
        "source": "prydwen.gg",
        "total": len(chars)
    }
    with open(WEEKLY_FILE,"w",encoding="utf-8") as f: json.dump(weekly,f,ensure_ascii=False,indent=2)
    print(f"=== 완료 {len(chars)}명, 변경 {len(changed_for_weekly)}명 ===")

if __name__=="__main__":
    main()
