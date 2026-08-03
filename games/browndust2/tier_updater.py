#!/usr/bin/env python3
# tiermaker_mapper.py - Tiermaker 파일명 그대로 매핑, 없으면 빈 문자열
import json, re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
ASSET_DIR = SCRIPT_DIR / "assets/images"
CHAR_PATH = DATA_DIR / "characters.json"

BASE_URL = "https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/"

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+','-',s)
    return re.sub(r'^-+|-+$','',s)

def normalize(s):
    return re.sub(r'[^a-z0-9]','',s.lower())

# 빌드 인덱스 (Tiermaker에 있는 실제 파일들)
idx_full = {}
idx_norm = {}
files = []
if ASSET_DIR.exists():
    for f in ASSET_DIR.iterdir():
        if f.suffix.lower() not in ['.png','.webp','.jpg','.jpeg']: continue
        if re.match(r'^\d{6,}-', f.name): continue
        idx_full[f.stem.lower()] = f.name
        n = normalize(f.stem)
        if n not in idx_norm:
            idx_norm[n] = f.name
        files.append(f.name)

print(f"[INDEX] Tiermaker 파일 {len(files)}개")

chars = json.loads(CHAR_PATH.read_text(encoding='utf-8'))
print(f"[LOAD] {len(chars)}개 캐릭터")

fixed = 0
missing = []

for c in chars:
    cid = c.get('id','')
    base = c.get('base_en','') or c.get('name_en','') or ''
    costume = c.get('costume','') or ''

    # Tiermaker 패턴: costume-base (예: b-rank-idol-helena)
    candidates = []
    if costume and base:
        candidates.append(slugify(f"{costume}-{base}"))
        candidates.append(slugify(f"{costume}{base}"))
    if cid:
        candidates.append(cid)
        candidates.append(slugify(cid))

    candidates = list(dict.fromkeys(candidates))

    found = None
    for cand in candidates:
        if cand.lower() in idx_full:
            found = idx_full[cand.lower()]
            break
        nc = normalize(cand)
        if nc in idx_norm:
            found = idx_norm[nc]
            break

    if found:
        c['image'] = BASE_URL + found
        fixed += 1
    else:
        # 없으면 빈 문자열 (fallback 없음)
        c['image'] = ""
        missing.append(cid)

print(f"[RESULT] 매핑 성공 {fixed}개, 없음 {len(missing)}개")
if missing:
    print("  없는 것들:")
    for m in missing[:30]:
        print(f"   - {m}")

# 저장
CHAR_PATH.write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"[SAVE] {CHAR_PATH}")
