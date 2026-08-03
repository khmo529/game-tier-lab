#!/usr/bin/env python3
# games/browndust2/tiermaker_mapper.py - v15.1 Safe Mapper
# Tiermaker 파일명 그대로 매핑, 없으면 빈 문자열
# 중요: 기존 이미지가 정상이면 절대 덮어쓰지 않음

import json, re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
CHAR_PATH = DATA_DIR / "characters.json"

# 배포 경로까지 탐색
CANDIDATE_ASSET_DIRS = [
    SCRIPT_DIR / "assets/images",
    Path(__file__).resolve().parents[2] / "wp-content/themes/generatepress-child/browndust2-tier/assets/images",
]

BASE_URL = "https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/"

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+','-',s)
    return re.sub(r'^-+|-+$','',s)

def normalize(s):
    return re.sub(r'[^a-z0-9]','',s.lower())

def build_index():
    idx_full = {}
    idx_norm = {}
    files = []
    found_dir = None
    for adir in CANDIDATE_ASSET_DIRS:
        if adir.exists():
            found_dir = adir
            for f in adir.iterdir():
                if f.suffix.lower() not in ['.png','.webp','.jpg','.jpeg']:
                    continue
                if re.match(r'^\d{6,}-', f.name):
                    continue
                if f.name.startswith('zzz'):
                    continue
                idx_full[f.stem.lower()] = f.name
                n = normalize(f.stem)
                if n not in idx_norm:
                    idx_norm[n] = f.name
                files.append(f.name)
            break
    print(f"[INDEX] {found_dir} - {len(files)}개")
    return idx_full, idx_norm

idx_full, idx_norm = build_index()

chars = json.loads(CHAR_PATH.read_text(encoding='utf-8'))
print(f"[LOAD] {len(chars)}개 캐릭터")

fixed = 0
kept = 0
missing = []

for c in chars:
    cid = c.get('id','')
    current = c.get('image','') or ''
    is_fallback = 'justia.png' in current and cid != 'justia' and 'knight-of-blood' not in cid and 'justia' not in cid
    is_empty = not current.strip()

    # v15 원칙: 정상 이미지는 스킵
    if not is_empty and not is_fallback:
        kept += 1
        continue

    base = c.get('base_en','') or c.get('name_en','') or ''
    costume = c.get('costume','') or ''

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
        c['image'] = ""  # 요청사항: 없으면 빈 문자열
        missing.append(cid)

print(f"[RESULT] 유지 {kept}개, 매핑 성공 {fixed}개, 없음 {len(missing)}개")
if missing:
    print("  없는 것들:")
    for m in missing[:30]:
        print(f"   - {m}")

CHAR_PATH.write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"[SAVE] {CHAR_PATH}")
