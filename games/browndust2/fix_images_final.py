
#!/usr/bin/env python3
# fix_images_final.py - 실제 파일명 그대로 쓰는 최종 fix
import json, re
from pathlib import Path

BASE_URL = "https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/"

def normalize(s):
    return re.sub(r'[^a-z0-9]','', s.lower())

def find_asset_dir():
    cur = Path(__file__).resolve().parent
    root = cur
    for _ in range(6):
        cand = root / "wp-content" / "themes" / "generatepress-child" / "browndust2-tier" / "assets" / "images"
        if cand.exists():
            return cand
        if (root / ".git").exists():
            if cand.exists():
                return cand
        root = root.parent
    # fallback
    cand = cur / "assets" / "images"
    if cand.exists():
        return cand
    # last resort rglob
    for p in Path.cwd().rglob("browndust2-tier/assets/images"):
        if p.is_dir():
            return p
    return None

def build_index(asset_dir):
    idx_full = {}
    idx_norm = {}
    files = []
    for f in asset_dir.iterdir():
        if f.suffix.lower() not in ['.png','.jpg','.jpeg','.webp']:
            continue
        if f.name.startswith('zzz') or re.match(r'^\d{6,}-', f.name):
            continue
        idx_full[f.stem.lower()] = f.name
        idx_norm[normalize(f.stem)] = f.name
        files.append(f.name)
    return idx_full, idx_norm, files

def find_best(char_id, base_en, costume, idx_full, idx_norm, files):
    cands = []
    if costume and base_en:
        cands.append(f"{costume}{base_en}")
        cands.append(f"{base_en}{costume}")
        cands.append(f"{costume}-{base_en}")
        cands.append(f"{base_en}-{costume}")
    if char_id:
        cands.append(char_id)
    if base_en:
        cands.append(base_en)
    
    # 1. normalize exact
    for cand in cands:
        n = normalize(cand)
        if n in idx_norm:
            return idx_norm[n]
        if cand.lower() in idx_full:
            return idx_full[cand.lower()]
    
    # 2. contains
    for cand in cands:
        cn = normalize(cand)
        for f in files:
            fn = normalize(f)
            if cn in fn or fn in cn:
                return f
    
    # 3. token overlap
    best=None
    best_score=0
    for cand in cands:
        cand_tokens = [t for t in re.split(r'[^a-z0-9]+', cand.lower()) if len(t)>2]
        for f in files:
            f_tokens = [t for t in re.split(r'[^a-z0-9]+', Path(f).stem.lower()) if len(t)>2]
            score = len(set(cand_tokens) & set(f_tokens))
            # bonus if base_en in file
            if base_en and base_en.lower() in f.lower():
                score+=1
            if score>best_score:
                best_score=score
                best=f
    if best_score>=1:
        return best
    return None

def main():
    # find characters.json
    script_dir = Path(__file__).resolve().parent
    possible = [
        script_dir / "data" / "characters.json",
        script_dir / "games" / "browndust2" / "data" / "characters.json",
        Path.cwd() / "games" / "browndust2" / "data" / "characters.json",
    ]
    char_path=None
    for p in possible:
        if p.exists():
            char_path=p
            break
    if not char_path:
        for p in Path.cwd().rglob("games/browndust2/data/characters.json"):
            char_path=p
            break
    if not char_path:
        print("characters.json 못 찾음")
        return
    
    asset_dir = find_asset_dir()
    if not asset_dir:
        print("asset dir 못 찾음")
        return
    
    idx_full, idx_norm, files = build_index(asset_dir)
    print(f"[INDEX] {asset_dir} - {len(files)}개")
    
    chars = json.loads(char_path.read_text(encoding='utf-8'))
    print(f"[LOAD] {len(chars)}개")
    
    fixed=0
    kept=0
    missing=[]
    for c in chars:
        cid=c.get('id','')
        base=c.get('base_en','') or c.get('name_en','') or ''
        costume=c.get('costume','') or ''
        cur=c.get('image','') or ''
        cur_file = Path(cur).name if cur else ''
        if cur_file in files:
            kept+=1
            continue
        
        best=find_best(cid, base, costume, idx_full, idx_norm, files)
        if best:
            c['image']=BASE_URL+best
            fixed+=1
        else:
            if cur_file not in files:
                c['image']=""
            missing.append(f"{cid} | base={base} costume={costume}")
    
    print(f"[RESULT] 유지 {kept}, 수정 {fixed}, 없음 {len(missing)}")
    for m in missing[:30]:
        print(f" - {m}")
    
    char_path.write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[SAVE] {char_path}")
    
    # wp 배포본도
    for _ in range(6):
        root = char_path
        for _ in range(6):
            wp = root.parent
            for __ in range(6):
                cand = wp / "wp-content" / "themes" / "generatepress-child" / "browndust2-tier" / "data" / "characters.json"
                if cand.exists() and cand != char_path:
                    cand.write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding='utf-8')
                    print(f"[SAVE WP] {cand}")
                    break
                wp = wp.parent
            break

if __name__=="__main__":
    main()
