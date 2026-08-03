#!/usr/bin/env python3
# tier_updater v15.1 - v15 + 이미지 자동 복구 버전
# - 기존 v15 원칙 유지: 등급만 업데이트
# - 추가: image가 justia.png거나 실제 파일이 없으면 assets 폴더에서 스마트 매칭으로 복구

import json, re, os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"

# assets 폴더 2군데 다 체크 (games 폴더에서 실행 / 워드프레스 폴더에서 실행 둘 다 대응)
POSSIBLE_ASSET_DIRS = [
    Path(__file__).resolve().parent.parent.parent / "wp-content/themes/generatepress-child/browndust2-tier/assets/images",
    SCRIPT_DIR.parent / "wp-content/themes/generatepress-child/browndust2-tier/assets/images",
    SCRIPT_DIR / "assets/images",
    Path.cwd() / "wp-content/themes/generatepress-child/browndust2-tier/assets/images",
    Path("/home/runner/work/game-tier-lab/game-tier-lab/wp-content/themes/generatepress-child/browndust2-tier/assets/images"),
]

KST = ZoneInfo("Asia/Seoul")
BASE_IMAGE_URL = "https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/"

def load_json(path, default):
    if not path.exists(): return default
    try: return json.loads(path.read_text(encoding='utf-8'))
    except: return default

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+','-',s)
    return re.sub(r'^-+|-+$','',s)

def normalize(s):
    return re.sub(r'[^a-z0-9]', '', s.lower()) if s else ""

def get_asset_dir():
    for d in POSSIBLE_ASSET_DIRS:
        if d.exists() and d.is_dir():
            return d
    # fallback: games/browndust2/data 기준 상대
    return DATA_DIR.parent / "assets/images"

def build_image_index(asset_dir):
    """폴더에 있는 실제 파일들로 인덱스 생성 - 네가 스크린샷에 올린 그 폴더"""
    index_full = {} # acting-archbishop-michaela -> file
    index_norm = {} # actingarchbishopmichaela -> file
    files = []
    if not asset_dir.exists():
        print(f"[WARN] Asset dir not found: {asset_dir}")
        return index_full, index_norm, files
    
    for f in asset_dir.iterdir():
        if f.is_file() and f.suffix.lower() in ['.png','.webp','.jpg','.jpeg']:
            if re.match(r'^\d{6,}-\d+\.', f.name): continue # 쓰레기 파일 스킵
            name = f.stem.lower()
            full_key = name
            norm_key = normalize(name)
            files.append(f.name)
            if full_key not in index_full:
                index_full[full_key] = f.name
            if norm_key not in index_norm:
                index_norm[norm_key] = f.name
    print(f"[IMAGE INDEX] {len(files)}개 파일 인덱싱 in {asset_dir}")
    # print 샘플 5개
    for k in list(index_full.keys())[:5]:
        print(f"  - {k} -> {index_full[k]}")
    return index_full, index_norm, files

def find_image_for_char(char, index_full, index_norm):
    """캐릭터 하나에 대해 실제 이미지 파일 찾기"""
    char_id = char.get('id','')
    base_en = char.get('base_en','') or char.get('name_en','')
    costume = char.get('costume','')
    
    candidates = []
    if char_id: candidates.append(char_id)
    if base_en and costume:
        candidates.append(slugify(f"{base_en}-{costume}"))
        candidates.append(slugify(f"{costume}-{base_en}"))
        candidates.append(slugify(f"{base_en}{costume}"))
        candidates.append(slugify(f"{costume}{base_en}"))
    if base_en: candidates.append(slugify(base_en))
    if costume: candidates.append(slugify(costume))
    # id 뒤집기
    if char_id and '-' in char_id:
        parts = char_id.split('-')
        candidates.append(''.join(parts))
        candidates.append('-'.join(reversed(parts)))
        candidates.append(''.join(reversed(parts)))

    candidates = list(dict.fromkeys([c.lower() for c in candidates if c]))

    for cand in candidates:
        full = cand.lower()
        norm = normalize(cand)
        if full in index_full:
            return index_full[full]
        if norm in index_norm:
            return index_norm[norm]
    return None

def main():
    asset_dir = get_asset_dir()
    index_full, index_norm, files = build_image_index(asset_dir)

    chars = load_json(CHAR_PATH, [])
    if not chars:
        print("[ERROR] characters.json 없음")
        return
    print(f"[BD2 v15.1] 기존 캐릭터 {len(chars)}개 로드")

    # 1. 이미지 복구 (핵심)
    fixed = 0
    still_missing = []
    for c in chars:
        current_img = c.get('image','')
        # justia.png거나, 비어있거나, 실제 파일이 없는 URL이면 복구 시도
        is_justia = 'justia.png' in current_img.lower()
        # 파일명 추출
        current_filename = ""
        if current_img:
            # URL에서 파일명 추출
            m = re.search(r'/([^/]+\.(png|webp|jpg))', current_img, re.I)
            if m:
                current_filename = m.group(1).lower()
        
        # 현재 이미지가 justia이거나, 인덱스에 없는 파일이면 복구
        need_fix = is_justia or not current_filename or (current_filename.lower() not in [f.lower() for f in files] and normalize(current_filename.replace('.png','')) not in index_norm)
        
        # 좀 더 엄격: justia가 아니더라도 id와 매칭되는 더 정확한 파일이 있으면 교체
        # 예: 현재가 actingarchbishopmichaela.png인데 id가 michaela-acting-archbishop이면, id에 더 가까운 파일이 있는지 체크
        # -> 일단 justia거나 파일 없는 경우만 고치자

        if need_fix:
            found = find_image_for_char(c, index_full, index_norm)
            if found:
                old = c.get('image')
                c['image'] = BASE_IMAGE_URL + found
                fixed += 1
                if fixed <= 20:
                    print(f"  [IMAGE FIX] {c['id']} : {old} -> {found}")
            else:
                still_missing.append(c['id'])

    print(f"[IMAGE] 복구 {fixed}개, 여전히 못 찾음 {len(still_missing)}개")
    if still_missing[:10]:
        print(f"  예시: {still_missing[:10]}")

    # 2. 외부 티어 (기존 로직 유지 - 지금은 실패해도 상관없음)
    # 등급 업데이트는 기존 파일 유지

    # 3. 저장
    CHAR_PATH.write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[BD2] characters.json 저장: {len(chars)}개 (이미지 {fixed}개 복구)")

    # 4. weekly 갱신
    counter = Counter(c.get('grade') or 'C' for c in chars)
    now = datetime.now(KST)
    meta = "전체 %d개 / " % len(chars) + " ".join(f"{t}:{counter[t]}" for t in ['SS+','SS','S','A','B','C'] if t in counter)
    weekly = load_json(WEEKLY_PATH, {})
    weekly.update({
        "version": f"{now.year}년 {now.month:02d}월 {(now.day-1)//7+1}주차 (W{now.isocalendar()[1]})",
        "updated": now.strftime("%Y-%m-%d"),
        "updated_at": now.isoformat(),
        "meta": meta,
        "total": len(chars),
        "grades": dict(counter),
    })
    WEEKLY_PATH.write_text(json.dumps(weekly, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[BD2] weekly: {meta}")

if __name__ == "__main__":
    main()
