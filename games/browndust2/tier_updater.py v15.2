#!/usr/bin/env python3
# tier_updater.py v15.2 - Safe + Robust Asset Search + Suffix Match
import json, re, sys
from pathlib import Path
from collections import Counter
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"
BASE_URL = "https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/"

def slugify(s):
    return re.sub(r'^-+|-+$','', re.sub(r'[^a-z0-9]+','-', s.lower()))

def normalize(s):
    return re.sub(r'[^a-z0-9]','', s.lower())

def find_asset_dir():
    # repo root 찾기 (games/browndust2 -> repo)
    repo_root = SCRIPT_DIR
    for _ in range(5):
        if (repo_root / "wp-content").exists() or (repo_root / ".git").exists():
            break
        repo_root = repo_root.parent
    
    candidates = [
        SCRIPT_DIR / "assets/images",
        repo_root / "wp-content/themes/generatepress-child/browndust2-tier/assets/images",
        repo_root / "games/browndust2/assets/images",
        Path.cwd() / "wp-content/themes/generatepress-child/browndust2-tier/assets/images",
    ]
    # rglob로 최후 보루
    for c in candidates:
        if c.exists():
            return c
    # 마지막으로 어디든 browndust2-tier/assets/images 찾아보기
    for p in repo_root.rglob("browndust2-tier/assets/images"):
        if p.is_dir():
            return p
    return None

def build_index():
    asset_dir = find_asset_dir()
    idx_full = {}
    idx_norm = {}
    idx_suffix = []  # (stem, filename) for suffix match
    files = []
    if asset_dir and asset_dir.exists():
        for f in asset_dir.iterdir():
            if f.suffix.lower() not in ['.png','.webp','.jpg','.jpeg']:
                continue
            if re.match(r'^\d{6,}-', f.name):
                continue
            if f.name.startswith('zzz'):
                continue
            stem = f.stem.lower()
            idx_full[stem] = f.name
            n = normalize(stem)
            if n not in idx_norm:
                idx_norm[n] = f.name
            idx_suffix.append((stem, f.name))
            files.append(f.name)
    print(f"[INDEX] {asset_dir} 에서 {len(files)}개")
    if len(files) == 0:
        print("[WARN] 이미지 인덱스 0개! 경로 확인 필요")
    return idx_full, idx_norm, idx_suffix, asset_dir

def fetch_tiers():
    if not requests:
        return {}
    return {}  # 외부 크롤링 실패시 등급 유지

def update_grades_only(chars, name_to_grade):
    if not name_to_grade:
        print("[SKIP] 외부 등급 없음")
        return 0
    updated=0
    for c in chars:
        # 기존 등급만
        pass
    return updated

def fill_missing_images_safe(chars, idx_full, idx_norm, idx_suffix):
    fixed=0
    kept=0
    missing=[]
    for c in chars:
        cid = c.get('id','')
        cur = c.get('image','') or ''
        is_fallback = ('justia.png' in cur and cid not in ['justia','justia-knight-of-blood','justia-blade-dancer']) and cur != ''
        is_empty = not cur.strip()

        if not is_empty and not is_fallback:
            kept+=1
            continue

        base = c.get('base_en','') or c.get('name_en','') or ''
        costume = c.get('costume','') or ''
        candidates=[]
        if costume and base:
            candidates.append(slugify(f"{costume}-{base}"))
            candidates.append(slugify(f"{costume}{base}"))
        if cid:
            candidates.append(cid.lower())
            candidates.append(slugify(cid))
        if base:
            candidates.append(base.lower())
            candidates.append(slugify(base))

        # 중복 제거 유지 순서
        candidates = list(dict.fromkeys(candidates))
        found=None

        # 1. 정확 일치
        for cand in candidates:
            if cand.lower() in idx_full:
                found = idx_full[cand.lower()]
                break
            if normalize(cand) in idx_norm:
                found = idx_norm[normalize(cand)]
                break

        # 2. suffix 매칭 (예: olstein -> archmage-olstein)
        if not found:
            for cand in candidates:
                cand_n = normalize(cand)
                for stem, fname in idx_suffix:
                    if stem.endswith(cand.lower()) or normalize(stem).endswith(cand_n):
                        # 가장 짧은 매칭 우선 (예: justia.png가 archmage-olstein보다 우선)
                        if found is None or len(stem) < len(found):
                            found = fname
                if found:
                    break

        # 3. 특수 베이스 캐릭터 fallback
        if not found:
            if cid == 'justia' or normalize(cid) == 'justia':
                if 'justia.png' in idx_full.values() or 'justia' in idx_full:
                    found = idx_full.get('justia', 'justia.png')
            if cid == 'olstein' or 'olstein' in cid:
                # olstein 베이스는 archmage-olstein.png로 대체
                for stem,fname in idx_suffix:
                    if 'olstein' in stem:
                        found = fname
                        break

        if found:
            c['image'] = BASE_URL + found
            fixed+=1
        else:
            # v15.2 원칙: 그래도 없으면 빈 문자열 유지 (justia 남용 금지)
            # 단, 베이스 캐릭터 justia/olstein은 빈 문자열로 두지 않고 로그만
            c['image'] = "" if cid not in ['justia','olstein'] else cur or ""
            missing.append(f"{cid} -> {candidates[0] if candidates else ''}")

    print(f"[IMAGE] 유지 {kept}개, 매핑 성공 {fixed}개, 없음 {len(missing)}개")
    for m in missing[:30]:
        print(f"   - {m} -> 빈 문자열 유지")
    return fixed, missing

def main():
    chars = json.loads(CHAR_PATH.read_text(encoding='utf-8'))
    print(f"[LOAD] {len(chars)}개")
    idx_full, idx_norm, idx_suffix, asset_dir = build_index()
    name_to_grade = fetch_tiers()
    # 등급 업데이트 (현재는 스킵)
    # generate weekly
    grades = [c.get('grade','B') for c in chars]
    counter = Counter(grades)
    total=len(chars)
    meta = f"전체 {total}개 / " + " ".join([f"{g}:{c}" for g,c in counter.items()])
    weekly = {
        "version": datetime.now().strftime("%Y년 %m월 %d주차 (W%V)").replace("%V", datetime.now().strftime("%V")),
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "meta": meta,
        "total": total,
        "grades": dict(counter),
        "buff": [], "nerf": [], "note": "Counter(c['grade']) 기준"
    }
    WEEKLY_PATH.write_text(json.dumps(weekly, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[WEEKLY] 저장: {meta}")

    fill_missing_images_safe(chars, idx_full, idx_norm, idx_suffix)

    CHAR_PATH.write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[SAVE] {CHAR_PATH}")

if __name__ == "__main__":
    main()
