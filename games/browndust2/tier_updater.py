#!/usr/bin/env python3
# games/browndust2/tier_updater.py - v15.1 Safe (Image Preservation + Tiermaker Mapper)
# 원칙: 이미지는 절대 안 건드린다. 등급만 업데이트한다. 없으면 빈 문자열.

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

# 이미지 폴더 2곳 탐색: 로컬 games 폴더 + WordPress 배포 폴더
CANDIDATE_ASSET_DIRS = [
    SCRIPT_DIR / "assets/images",
    Path(__file__).resolve().parents[2] / "wp-content/themes/generatepress-child/browndust2-tier/assets/images",
    Path(__file__).resolve().parents[3] / "wp-content/themes/generatepress-child/browndust2-tier/assets/images", # actions runner에서 depth 다를 수 있음
]

BASE_URL = "https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/"

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return re.sub(r'^-+|-+$', '', s)

def normalize(s: str) -> str:
    return re.sub(r'[^a-z0-9]', '', s.lower())

def load_characters():
    if not CHAR_PATH.exists():
        print(f"[ERROR] {CHAR_PATH} 없음")
        sys.exit(1)
    chars = json.loads(CHAR_PATH.read_text(encoding='utf-8'))
    print(f"[LOAD] {len(chars)}개 캐릭터 로드")
    return chars

def build_asset_index():
    """Tiermaker에 있는 실제 파일 인덱스 (zzz, 숫자 prefix 제외)"""
    idx_full = {}
    idx_norm = {}
    asset_dir_found = None
    files = []
    for adir in CANDIDATE_ASSET_DIRS:
        if adir.exists():
            asset_dir_found = adir
            for f in adir.iterdir():
                if f.suffix.lower() not in ['.png','.webp','.jpg','.jpeg']:
                    continue
                if re.match(r'^\d{6,}-', f.name): # tiermaker 임시 파일 제외
                    continue
                if f.name.startswith('zzz'):
                    continue
                idx_full[f.stem.lower()] = f.name
                n = normalize(f.stem)
                if n not in idx_norm:
                    idx_norm[n] = f.name
                files.append(f.name)
            break
    print(f"[INDEX] {asset_dir_found} 에서 {len(files)}개 이미지 인덱스")
    return idx_full, idx_norm, asset_dir_found

def fetch_tiers_pocket_tactics():
    """외부 티어 크롤링 - 실패 시 빈 dict 반환 (등급 보존)"""
    if not requests:
        print("[WARN] requests/bs4 없음, 크롤링 스킵")
        return {}
    url = "https://www.pockettactics.com/brown-dust-2/tier-list"
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        # 예시 파서 - 실제 DOM에 맞게 수정 필요
        # Pocket Tactics는 보통 h3 등급 + ul li 캐릭터명 구조
        name_to_grade = {}
        # TODO: 실제 셀렉터에 맞게 교체
        # 아래는 안전한 fallback 예시 - 못 찾으면 그대로 둠
        print(f"[CRAWL] {url} 크롤링 성공 (파서 구현 필요)")
        return name_to_grade
    except Exception as e:
        print(f"[CRAWL FAIL] {e} - 기존 등급 유지")
        return {}

def update_grades_only(chars, name_to_grade):
    """v15 핵심: grade만 업데이트, image 절대 안 건드림"""
    updated = 0
    for c in chars:
        cid = c.get('id','')
        base = c.get('base_en','') or ''
        costume = c.get('costume','') or ''
        # 매칭 후보: id, base+costume slug, normalize
        candidates = []
        if cid:
            candidates.append(cid.lower())
            candidates.append(normalize(cid))
        if base and costume:
            candidates.append(slugify(f"{costume}-{base}").lower())
            candidates.append(normalize(f"{costume}{base}"))
        if base:
            candidates.append(base.lower())
            candidates.append(normalize(base))

        found_grade = None
        for cand in candidates:
            if cand in name_to_grade:
                found_grade = name_to_grade[cand]
                break
            # normalize 맵도 확인
            nc = normalize(cand)
            if nc in name_to_grade:
                found_grade = name_to_grade[nc]
                break

        if found_grade and c.get('grade') != found_grade:
            print(f"  [GRADE] {cid}: {c.get('grade')} -> {found_grade}")
            c['grade'] = found_grade
            # 선택적: pve/pvp 점수도 같이 갱신한다면 여기서만
            # c['score'] = ...
            updated += 1
    print(f"[RESULT] 등급 업데이트 {updated}개")
    return updated

def fill_missing_images_safe(chars, idx_full, idx_norm):
    """
    v15.1 + Tiermaker 통합 규칙:
    - 이미지가 정상이면 절대 안 건드림
    - 이미지가 비어있거나 justia.png fallback이거나 로컬에 없는 경우에만 Tiermaker 파일로 매핑
    - 없으면 빈 문자열 (fallback 남용 금지)
    """
    fixed = 0
    missing = []
    for c in chars:
        cid = c.get('id','')
        current_img = c.get('image','') or ''
        # 정상 이미지인지 판단
        is_fallback = 'justia.png' in current_img and cid != 'justia' and 'knight-of-blood' not in cid
        is_empty = not current_img.strip()
        # 로컬 파일 존재 여부 체크는 생략 - URL 기반이므로 fallback/empty만으로 판단 (v15 안전)

        if not is_empty and not is_fallback:
            continue  # v15 원칙: 건드리지 않음

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
            c['image'] = ""  # 빈 문자열 유지 (요청사항)
            missing.append(cid)

    print(f"[IMAGE SAFE] Tiermaker 매핑 성공 {fixed}개, 없음 {len(missing)}개")
    if missing:
        for m in missing[:20]:
            print(f"   - {m} -> 빈 문자열 유지")
    return fixed, missing

def generate_weekly(chars):
    """실제 DB Counter로 집계 - S:0 버그 방지"""
    grades = [c.get('grade','B') for c in chars]
    counter = Counter(grades)
    total = len(chars)
    # 정렬: SS+ > SS > S > A > B > C
    order = ["SS+", "SS", "S", "A", "B", "C", "D"]
    sorted_grades = {k: counter.get(k,0) for k in order if counter.get(k,0) > 0}
    # 나머지도 포함
    for k,v in counter.items():
        if k not in sorted_grades:
            sorted_grades[k]=v

    meta_str = f"전체 {total}개 / " + " ".join([f"{g}:{c}" for g,c in sorted_grades.items()])
    weekly = {
        "version": datetime.now().strftime("%Y년 %m월 %d주차 (W%V)").replace("%V", datetime.now().strftime("%V")),
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "meta": meta_str,
        "total": total,
        "grades": dict(counter),
        "buff": [],
        "nerf": [],
        "note": "자동 집계 - Counter(c['grade']) 기준"
    }
    WEEKLY_PATH.write_text(json.dumps(weekly, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[WEEKLY] {WEEKLY_PATH} 저장: {meta_str}")
    return weekly

def main():
    chars = load_characters()
    idx_full, idx_norm, asset_dir = build_asset_index()
    name_to_grade = fetch_tiers_pocket_tactics()

    if name_to_grade:
        update_grades_only(chars, name_to_grade)
    else:
        print("[SKIP] 외부 등급 없음 - grade 유지")

    # 이미지 보존형 매핑: 비어있는 것만 Tiermaker에서 채움
    fill_missing_images_safe(chars, idx_full, idx_norm)

    # 저장
    CHAR_PATH.write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[SAVE] {CHAR_PATH}")

    generate_weekly(chars)

if __name__ == "__main__":
    main()
