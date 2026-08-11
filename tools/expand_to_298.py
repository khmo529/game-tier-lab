
import os, glob, json
# 현재 폴더의 jpg 파일 목록으로 pals.json을 298개로 확장
IMAGE_DIR = "../palworld-tier/assets/images" if os.path.exists("../palworld-tier/assets/images") else "palworld-tier/assets/images"
PALS_JSON = "palworld-tier/data/pals.json"

files = glob.glob(os.path.join(IMAGE_DIR, "*.jpg"))
print(f"Found {len(files)} jpg files")
# 기존 pals 로드
with open(PALS_JSON,'r',encoding='utf-8') as f:
    pals=json.load(f)

existing_ko={p["ko"] for p in pals}
for fp in files:
    name=os.path.splitext(os.path.basename(fp))[0]
    if name not in existing_ko:
        pals.append({"id":name,"name":name,"ko":name,"element":["Neutral"],"tier":"B","type":"거점","work":"초반","work_level":{},"max_work":0,"desc":"OP.GG 298 자동추가","image_ko":f"{name}.jpg"})
        existing_ko.add(name)

print(f"Total after add: {len(pals)}")
with open(PALS_JSON,'w',encoding='utf-8') as f:
    json.dump(pals, f, ensure_ascii=False, indent=2)
