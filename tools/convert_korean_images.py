"""
한글 파일명 JPG 변환 툴 (V9)
- 입력: 다운로드 폴더에 있는 검구리.jpg, 까부냥.jpg ... 298개
- 출력: pals.json에서 ko 이름이 파일명과 일치하는 애들 image 경로를 한글 .jpg로 교체

사용법:
1. 네가 받은 폴더 (팰월드 팰 도감 - 전체 팰 스탯-스킬 _ OP.GG 2) 안에 있는 .jpg 파일들을
   wp-content/themes/generatepress-child/palworld-tier/assets/images/ 에 그대로 복사
2. python tools/convert_korean_images.py 실행

그러면 pals.json의 image 필드가 한글 파일명으로 자동 매핑됨
"""
import os, json, glob, re

# 한글 -> 영문/ID 매핑은 기존 pals.json의 ko 필드로 자동 매칭
PALS_JSON = "palworld-tier/data/pals.json"
IMAGE_DIR = "palworld-tier/assets/images"

def build():
    if not os.path.exists(PALS_JSON):
        print(f"{PALS_JSON} 없음")
        return
    with open(PALS_JSON,'r',encoding='utf-8') as f:
        pals=json.load(f)
    
    # 이미지 폴더에 있는 한글 jpg 목록
    files = glob.glob(os.path.join(IMAGE_DIR, "*.jpg")) + glob.glob(os.path.join(IMAGE_DIR, "*.JPG"))
    file_map = {os.path.splitext(os.path.basename(f))[0]: os.path.basename(f) for f in files}
    print(f"Found {len(file_map)} korean images: {list(file_map.keys())[:10]}")

    # ko 이름으로 매칭
    matched=0
    for p in pals:
        ko = p.get("ko","").strip()
        # 파일명에서 확장자 제외한 이름이 ko와 일치하면
        if ko in file_map:
            p["image_ko"] = file_map[ko]  # 검구리.jpg
            p["image"] = f"{IMAGE_DIR.replace('palworld-tier/','')}/{file_map[ko]}" # assets/images/검구리.jpg
            matched+=1
        # 변이종: 라일린 녹트 -> 라일린 녹트.jpg 또는 라일린녹트.jpg
        else:
            # 공백 제거 버전도 시도
            ko_nospace = ko.replace(" ","")
            if ko_nospace in file_map:
                p["image_ko"] = file_map[ko_nospace]
                matched+=1
            # 유사 매칭: 파일명에 ko가 포함되면
            else:
                for fname in file_map.keys():
                    if ko in fname or fname in ko:
                        p["image_ko"] = file_map[fname]
                        matched+=1
                        break

    print(f"Matched {matched}/{len(pals)}")

    with open(PALS_JSON,'w',encoding='utf-8') as f:
        json.dump(pals, f, ensure_ascii=False, indent=2)

    # last_update
    with open("palworld-tier/data/last_update.json","w",encoding="utf-8") as f:
        json.dump({"count":len(pals),"matched":matched,"note":"korean filename mapping"}, f, ensure_ascii=False, indent=2)

if __name__=="__main__":
    build()
