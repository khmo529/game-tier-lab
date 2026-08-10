
import requests, json, os, datetime

def fetch_paldeck_extended():
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
                if len(data)>50:
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

    if not raw:
        pals=existing
    else:
        id_map={p["id"].upper(): p for p in existing}
        pals=[]
        for entry in raw[:200]:
            try:
                pid = entry.get("id") or entry.get("no")
                if not pid: continue
                pid_str = f"{int(str(pid).replace('B','').replace('b','')):03d}"
                if entry.get("isVariant") or "B" in str(entry.get("name","")):
                    # 대문자 B 유지
                    if "B" in str(entry.get("id","")) or True:
                        # mlg404는 변이종 파일명이 012B.png
                        pid_str = pid_str + "B"
                ex = id_map.get(pid_str) or id_map.get(pid_str.replace("B","")) or {}
                pals.append({
                    "id": pid_str,
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
            except: continue
        # 기존에 있는데 raw에 없는 애들 (123B 같은 신팰) 유지
        existing_ids=set([p["id"].upper() for p in pals])
        for p in existing:
            if p["id"].upper() not in existing_ids:
                pals.append(p)

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
        "sources": ["mlg404/palworld-paldex-api (001.png, 012B.png)", "charles8ff/palworld-assets (123, 123B, 113 신팰 대응)", "wiki API 제거 - ERR_NAME_NOT_RESOLVED 해결"],
    }
    with open("games/palworld/data/last_update.json","w",encoding="utf-8") as f:
        json.dump(last,f,ensure_ascii=False,indent=2)
    with open("wp-content/themes/generatepress-child/palworld-tier/data/last_update.json","w",encoding="utf-8") as f:
        json.dump(last,f,ensure_ascii=False,indent=2)
    print(f"Done {len(pals)} - wiki API removed")

if __name__=="__main__":
    build()
