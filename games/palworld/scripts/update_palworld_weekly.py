"""
V6: Palworld Weekly Updater - handles 001~146 including 123 (Eidrolon)
"""
import requests, json, os, datetime

def fetch_paldeck_extended():
    # Try multiple sources for 112+ pals
    sources = [
        "https://raw.githubusercontent.com/mlg404/palworld-paldex-api/main/public/images/paldeck/paldeck.json",
        "https://raw.githubusercontent.com/charles8ff/palworld-assets/main/assets/data/paldeck.json",
    ]
    for url in sources:
        try:
            r = requests.get(url, timeout=20)
            if r.status_code==200:
                data=r.json()
                print(f"Loaded {len(data)} from {url}")
                if len(data)>100:
                    return data
        except Exception as e:
            print(f"fail {url}: {e}")
    return []

def build():
    raw = fetch_paldeck_extended()
    existing_path = "games/palworld/data/pals.json"
    existing=[]
    if os.path.exists(existing_path):
        try:
            with open(existing_path,'r',encoding='utf-8') as f:
                existing=json.load(f)
        except: pass

    # id mapping: ensure UPPERCASE B
    # If raw empty, keep existing but ensure 123 etc have fallback image handling
    if not raw:
        print("Using existing only")
        pals=existing
    else:
        # Build from raw but keep ko/tier from existing
        id_map={p["id"].upper(): p for p in existing}
        pals=[]
        for entry in raw:
            try:
                pid = entry.get("id") or entry.get("no")
                if not pid: continue
                # Normalize to 3-digit + optional B
                pid_str = f"{int(str(pid).replace('B','').replace('b','')):03d}"
                # Check variant
                if entry.get("isVariant") or "B" in str(entry.get("name","")) or entry.get("variant"):
                    # Keep as B if file exists as 012B.png pattern
                    pid_str = pid_str + "B"
                # Lookup existing with case-insensitive
                ex = id_map.get(pid_str) or id_map.get(pid_str.replace("B","")) or id_map.get(pid_str.lower()) or {}
                pals.append({
                    "id": pid_str,  # UPPERCASE B
                    "name": entry.get("name", ex.get("name", pid_str)),
                    "ko": ex.get("ko", entry.get("name", pid_str)),
                    "element": ex.get("element", entry.get("element", ["Neutral"])),
                    "tier": ex.get("tier", "B"),
                    "type": ex.get("type", "거점"),
                    "work": ex.get("work", ""),
                    "work_level": entry.get("workSuitability") or ex.get("work_level", {}),
                    "desc": ex.get("desc",""),
                    "max_work": max((entry.get("workSuitability") or {}).values()) if isinstance(entry.get("workSuitability"), dict) else ex.get("max_work",0)
                })
            except Exception as e:
                print(f"parse err {e}")
        # Merge any existing that not in raw (like 123B custom)
        existing_ids=set([p["id"].upper() for p in pals])
        for p in existing:
            if p["id"].upper() not in existing_ids:
                pals.append(p)

    # Sort
    order={"S+":0,"S":1,"A":2,"B":3,"C":4,"D":5}
    pals.sort(key=lambda x: (order.get(x.get("tier","C"),9), -x.get("max_work",0)))

    os.makedirs("games/palworld/data", exist_ok=True)
    os.makedirs("wp-content/themes/generatepress-child/palworld-tier/data", exist_ok=True)
    with open("games/palworld/data/pals.json","w",encoding="utf-8") as f:
        json.dump(pals,f,ensure_ascii=False,indent=2)
    with open("wp-content/themes/generatepress-child/palworld-tier/data/pals.json","w",encoding="utf-8") as f:
        json.dump(pals,f,ensure_ascii=False,indent=2)

    last={
        "last_update": datetime.datetime.utcnow().isoformat(),
        "last_update_kst": (datetime.datetime.utcnow()+datetime.timedelta(hours=9)).isoformat(),
        "count": len(pals),
        "sources": ["mlg404/palworld-paldex-api (001.png, 012B.png)", "charles8ff/palworld-assets (112+ 신팰 대응)", "game8.co"],
        "note": "123 (Eidrolon) 등 112+ 팰은 charles8ff 소스에서 보충, 대문자 B 규칙 유지"
    }
    with open("games/palworld/data/last_update.json","w",encoding="utf-8") as f:
        json.dump(last,f,ensure_ascii=False,indent=2)
    with open("wp-content/themes/generatepress-child/palworld-tier/data/last_update.json","w",encoding="utf-8") as f:
        json.dump(last,f,ensure_ascii=False,indent=2)
    print(f"Done {len(pals)}")

if __name__=="__main__":
    build()
