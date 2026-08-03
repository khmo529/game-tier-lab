#!/usr/bin/env python3
# tier_updater v16 FINAL - GitHub Action 전용, 이미지 자동 복구 + 다운로드까지
# 원칙: GitHub에서만 수정, Vultr는 건드리지 않음. Action이 다 해결.

import json, re, os, requests, shutil, difflib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
ASSET_DIR = SCRIPT_DIR / "assets/images"
WP_ASSET_DIR = SCRIPT_DIR / "../../wp-content/themes/generatepress-child/browndust2-tier/assets/images"

CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"

KST = ZoneInfo("Asia/Seoul")
BASE_IMAGE_URL = "https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/"
FANDOM_HEADERS = {"User-Agent": "Mozilla/5.0 (NoPickleBot/2.0)"}

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+','-',s)
    return re.sub(r'^-+|-+$','',s)

def normalize(s):
    return re.sub(r'[^a-z0-9]','',s.lower()) if s else ""

def load_json(path, default):
    if not path.exists(): return default
    try: return json.loads(path.read_text(encoding='utf-8'))
    except: return default

def build_index(asset_dir):
    idx_full, idx_norm = {}, {}
    files = []
    if not asset_dir.exists():
        asset_dir.mkdir(parents=True, exist_ok=True)
        return idx_full, idx_norm, files
    for f in asset_dir.iterdir():
        if not f.is_file(): continue
        if f.suffix.lower() not in ['.png','.webp','.jpg','.jpeg']: continue
        if re.match(r'^\d{6,}-\d+\.', f.name): continue # 쓰레기 파일 스킵
        stem = f.stem.lower()
        idx_full[stem] = f.name
        n = normalize(stem)
        if n not in idx_norm:
            idx_norm[n] = f.name
        files.append(f.name)
    return idx_full, idx_norm, files

def find_existing(char, idx_full, idx_norm):
    cid = char.get('id','')
    base = char.get('base_en','') or char.get('name_en','')
    costume = char.get('costume','')
    cands = []
    if cid: cands.append(cid)
    if base and costume:
        cands.append(slugify(f"{base}-{costume}"))
        cands.append(slugify(f"{costume}-{base}"))
        cands.append(slugify(f"{base}{costume}"))
        cands.append(slugify(f"{costume}{base}"))
    if base: cands.append(slugify(base))
    if costume: cands.append(slugify(costume))
    if cid and '-' in cid:
        parts = cid.split('-')
        cands.append(''.join(parts))
        cands.append('-'.join(reversed(parts)))
        cands.append(''.join(reversed(parts)))
    cands = list(dict.fromkeys([c.lower() for c in cands if c]))
    for cand in cands:
        if cand in idx_full:
            return idx_full[cand]
        nc = normalize(cand)
        if nc in idx_norm:
            return idx_norm[nc]
    # difflib 퍼지 매칭
    if cid:
        close = difflib.get_close_matches(cid, list(idx_full.keys()), n=1, cutoff=0.75)
        if close:
            return idx_full[close[0]]
        close_n = difflib.get_close_matches(normalize(cid), list(idx_norm.keys()), n=1, cutoff=0.75)
        if close_n:
            return idx_norm[close_n[0]]
    return None

def try_fandom_download(char_id, base_en, costume, save_dir):
    candidates = []
    if base_en and costume:
        candidates += [f"{base_en} {costume}", f"{costume} {base_en}", f"{base_en}-{costume}"]
    if base_en: candidates.append(base_en)
    candidates.append(char_id.replace('-',' '))
    candidates.append(char_id)
    for name in candidates:
        for ext in ['png','webp','jpg']:
            url = f"https://browndust2.fandom.com/wiki/Special:FilePath/{name}.{ext}"
            try:
                r = requests.get(url, headers=FANDOM_HEADERS, timeout=15, stream=True, allow_redirects=True)
                if r.status_code==200 and 'image' in r.headers.get('Content-Type','') and len(r.content) > 8000:
                    out_path = save_dir / f"{char_id}.png"
                    with open(out_path,'wb') as f:
                        for chunk in r.iter_content(8192):
                            f.write(chunk)
                    print(f"  [DL OK] {char_id}.png <- {name}.{ext} ({len(r.content)} bytes)")
                    return out_path.name
            except Exception:
                continue
    return None

def main():
    print(f"[PATH] {SCRIPT_DIR}")
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    WP_ASSET_DIR.mkdir(parents=True, exist_ok=True)

    idx_full, idx_norm, files = build_index(ASSET_DIR)
    print(f"[INDEX] {len(files)}개 이미지 인덱싱")

    chars = load_json(CHAR_PATH, [])
    if not chars:
        print(f"[ERROR] {CHAR_PATH} 없음")
        return
    print(f"[LOAD] 캐릭터 {len(chars)}개")

    fixed = 0
    downloaded = 0
    still = []

    for c in chars:
        cid = c.get('id','')
        cur_img = c.get('image','')
        need_fix = 'justia.png' in cur_img.lower() or not cur_img

        # 현재 이미지가 실제 파일이 아니면 무조건 복구 대상
        if not need_fix and cur_img:
            m = re.search(r'/([^/]+\.(png|webp|jpg))', cur_img, re.I)
            if m:
                fname = m.group(1).lower()
                if fname not in [f.lower() for f in files] and normalize(Path(fname).stem) not in idx_norm:
                    need_fix = True

        if not need_fix:
            continue

        # 1. 기존 파일에서 찾기
        found = find_existing(c, idx_full, idx_norm)
        if found:
            # 찾은 파일을 id.png로 복사해서 통일 (앞으로 매칭 100%)
            src = ASSET_DIR / found
            dst = ASSET_DIR / f"{cid}.png"
            if not dst.exists() and src.exists():
                try:
                    shutil.copy(src, dst)
                    print(f"  [COPY] {found} -> {cid}.png")
                    # 인덱스 업데이트
                    idx_full[cid] = f"{cid}.png"
                    idx_norm[normalize(cid)] = f"{cid}.png"
                    files.append(f"{cid}.png")
                    found = f"{cid}.png"
                except Exception:
                    pass
            c['image'] = BASE_IMAGE_URL + found
            fixed += 1
            continue

        # 2. 없으면 Fandom에서 다운로드
        dl = try_fandom_download(cid, c.get('base_en',''), c.get('costume',''), ASSET_DIR)
        if dl:
            c['image'] = BASE_IMAGE_URL + dl
            downloaded += 1
            # WP 폴더에도 복사 (Action에서 다시 복사하지만 미리)
            try:
                shutil.copy(ASSET_DIR / dl, WP_ASSET_DIR / dl)
            except Exception:
                pass
        else:
            still.append(cid)

    print(f"\n[RESULT] 기존 파일로 복구 {fixed}개, Fandom 다운로드 {downloaded}개, 남은 {len(still)}개")
    if still:
        print(f"  남은: {still[:20]}")

    # 저장
    CHAR_PATH.write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding='utf-8')

    # weekly 갱신
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
    print(f"[SAVE] {CHAR_PATH} / {WEEKLY_PATH}")

if __name__ == "__main__":
    main()
