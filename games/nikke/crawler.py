import json, re
FULL_EN_TO_KO = {... # 위에 200개 딕셔너리 그대로 복사
}

with open("characters.json", encoding="utf-8") as f:
    data=json.load(f)

trans={k.lower():v for k,v in FULL_EN_TO_KO.items()}
for c in data:
    if c.get("en_name") and re.search(r'[가-힣]', c.get("name","")):
        trans[c["en_name"].lower()]=c["name"]

dedup={}
for c in sorted(data, key=lambda x: 0 if x.get("company")!="미확인" else 1):
    key=(c.get("en_name") or c["name"]).lower()
    if key not in dedup:
        dedup[key]=c
    # 한글 강제
    if c.get("en_name","").lower() in trans:
        dedup[key]["name"]=trans[c.get("en_name","").lower()]

# 최종 한글화
for c in dedup.values():
    if not re.search(r'[가-힣]', c["name"]) and c.get("en_name","").lower() in trans:
        c["name"]=trans[c["en_name"].lower()]

with open("characters_fixed.json","w",encoding="utf-8") as f:
    json.dump(list(dedup.values()), f, ensure_ascii=False, indent=2)

print(f"기존 {len(data)}개 -> 정리 {len(dedup)}개")
print("남은 영어:", [c["name"] for c in dedup.values() if not re.search(r'[가-힣]', c["name"])][:20])
