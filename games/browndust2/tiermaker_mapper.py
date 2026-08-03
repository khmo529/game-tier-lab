#!/usr/bin/env python3
# tiermaker_mapper.py v15.2 - Robust
import json, re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
CHAR_PATH = DATA_DIR / "characters.json"
BASE_URL = "https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/"

def slugify(s):
    return re.sub(r'^-+|-+$','', re.sub(r'[^a-z0-9]+','-', s.lower()))

def normalize(s):
    return re.sub(r'[^a-z0-9]','', s.lower())

def find_asset_dir():
    repo_root = SCRIPT_DIR
    for _ in range(5):
        if (repo_root / "wp-content").exists() or (repo_root / ".git").exists():
            break
        repo_root = repo_root.parent
    cands = [
        SCRIPT_DIR / "assets/images",
        repo_root / "wp-content/themes/generatepress-child/browndust2-tier/assets/images",
    ]
    for c in cands:
        if c.exists():
            return c
    for p in repo_root.rglob("browndust2-tier/assets/images"):
        if p.is_dir():
            return p
    return None

def build_index():
    adir = find_asset_dir()
    idx_full={}
    idx_norm={}
    idx_suffix=[]
    if adir:
        for f in adir.iterdir():
            if f.suffix.lower() not in ['.png','.webp','.jpg','.jpeg']: continue
            if f.name.startswith('zzz'): continue
            if re.match(r'^\d{6,}-', f.name): continue
            stem=f.stem.lower()
            idx_full[stem]=f.name
            idx_norm[normalize(stem)]=f.name
            idx_suffix.append((stem,f.name))
    print(f"[INDEX] {adir} - {len(idx_full)}개")
    return idx_full, idx_norm, idx_suffix

idx_full, idx_norm, idx_suffix = build_index()
chars = json.loads(CHAR_PATH.read_text(encoding='utf-8'))
print(f"[LOAD] {len(chars)}개")

fixed=kept=0
missing=[]
for c in chars:
    cid=c.get('id','')
    cur=c.get('image','') or ''
    if cur.strip() and 'justia.png' not in cur:
        kept+=1
        continue
    # fallback이나 empty만 교체
    base=c.get('base_en','') or ''
    costume=c.get('costume','') or ''
    cands=[]
    if costume and base:
        cands.append(slugify(f"{costume}-{base}"))
    if cid:
        cands.append(cid.lower())
        cands.append(slugify(cid))
    if base:
        cands.append(base.lower())
    cands=list(dict.fromkeys(cands))
    found=None
    for cand in cands:
        if cand in idx_full:
            found=idx_full[cand]
            break
        if normalize(cand) in idx_norm:
            found=idx_norm[normalize(cand)]
            break
    if not found:
        for cand in cands:
            for stem,fname in idx_suffix:
                if stem.endswith(cand) or cand in stem:
                    found=fname
                    break
            if found:
                break
    if found:
        c['image']=BASE_URL+found
        fixed+=1
    else:
        c['image']=""
        missing.append(cid)

print(f"[RESULT] 유지 {kept}, 성공 {fixed}, 없음 {len(missing)}")
for m in missing[:20]:
    print(f" - {m}")
CHAR_PATH.write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding='utf-8')
