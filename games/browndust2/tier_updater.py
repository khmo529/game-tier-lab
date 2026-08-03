#!/usr/bin/env python3
# fix_remaining_39.py - 남은 39개 이미지 Fandom에서 다운로드 + 오타 매칭
import json, re, os, requests, difflib
from pathlib import Path

BASE_DIR = Path("/home/nopickle/htdocs/nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier")
DATA_DIR = BASE_DIR / "data" if (BASE_DIR / "data").exists() else BASE_DIR / "../data"
CHAR_PATH = BASE_DIR / "data/characters.json" if (BASE_DIR / "data/characters.json").exists() else Path("data/characters.json")
ASSET_DIR = BASE_DIR / "assets/images"

BASE_URL = "https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/"
FANDOM_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NoPickleBot/2.0)"}

def normalize(s): return re.sub(r'[^a-z0-9]', '', s.lower())

def load_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

# Fandom에서 이미지 다운로드 시도
def try_fandom_download(char_id, base_en, costume):
    candidates = []
    if base_en and costume:
        candidates += [
            f"{base_en} {costume}",
            f"{costume} {base_en}",
            f"{base_en} {costume}".replace('-',' '),
            f"{base_en}_{costume}",
            f"{base_en}({costume})",
        ]
    if base_en:
        candidates.append(base_en)
    candidates.append(char_id.replace('-',' '))
    candidates.append(char_id)

    for name in candidates:
        for ext in ['png','webp','jpg']:
            # Special:FilePath는 대소문자 구분 덜 함
            url = f"https://browndust2.fandom.com/wiki/Special:FilePath/{name}.{ext}"
            try:
                r = requests.get(url, headers=FANDOM_HEADERS, timeout=10, stream=True, allow_redirects=True)
                if r.status_code == 200 and 'image' in r.headers.get('Content-Type',''):
                    # 너무 작은 파일(404 html)은 제외
                    if len(r.content) < 5000:
                        continue
                    out_path = ASSET_DIR / f"{char_id}.png"
                    with open(out_path, 'wb') as f:
                        for chunk in r.iter_content(8192):
                            f.write(chunk)
                    print(f"  [DOWNLOAD OK] {char_id}.png <- {name}.{ext} ({len(r.content)} bytes)")
                    return out_path.name
            except Exception as e:
                continue
    return None

# 메인
chars = load_json(CHAR_PATH)
files = [f.name for f in ASSET_DIR.iterdir() if f.suffix.lower() in ['.png','.webp','.jpg']]
files_stem = [f.lower() for f in files]
norm_map = {normalize(Path(f).stem): f for f in files}

print(f"[INFO] 현재 이미지 {len(files)}개, 캐릭터 {len(chars)}개")

missing = []
for c in chars:
    img = c.get('image','')
    # justia로 떨어지거나 파일이 실제로 없는 경우
    if 'justia.png' in img.lower():
        missing.append(c)
    else:
        # URL에서 파일명 추출해서 실제로 존재하는지 체크
        m = re.search(r'/([^/]+\.(png|webp|jpg))', img, re.I)
        if m:
            fname = m.group(1)
            if fname.lower() not in files_stem and normalize(Path(fname).stem) not in norm_map:
                missing.append(c)

print(f"[MISSING] {len(missing)}개 남음")
for c in missing[:15]:
    print(f" - {c['id']} | base={c.get('base_en')} costume={c.get('costume')} | current={c.get('image').split('/')[-1]}")

# 1단계: 오타/유사 매칭으로 기존 파일 재활용
fixed = 0
for c in missing[:]:
    cid = c['id']
    # difflib로 가장 가까운 파일 찾기
    close = difflib.get_close_matches(cid, [f.lower().replace('.png','') for f in files], n=1, cutoff=0.7)
    if not close:
        # 정규화 버전으로도 시도
        norm_cid = normalize(cid)
        close_norm = difflib.get_close_matches(norm_cid, list(norm_map.keys()), n=1, cutoff=0.7)
        if close_norm:
            matched_file = norm_map[close_norm[0]]
            # 복사해서 정확한 id로 만들기
            src = ASSET_DIR / matched_file
            dst = ASSET_DIR / f"{cid}.png"
            if not dst.exists():
                import shutil
                shutil.copy(src, dst)
                print(f"  [COPY] {matched_file} -> {cid}.png (유사도 {close_norm[0]})")
                c['image'] = BASE_URL + f"{cid}.png"
                fixed += 1
                missing.remove(c)
            continue
    else:
        # 찾았으면 복사
        matched_stem = close[0]
        # 실제 파일명 찾기
        actual = next((f for f in files if f.lower().startswith(matched_stem) or matched_stem in f.lower()), None)
        if actual:
            import shutil
            src = ASSET_DIR / actual
            dst = ASSET_DIR / f"{cid}.png"
            if not dst.exists():
                shutil.copy(src, dst)
                print(f"  [COPY] {actual} -> {cid}.png")
                c['image'] = BASE_URL + f"{cid}.png"
                fixed += 1
                if c in missing:
                    missing.remove(c)

print(f"\n[COPY FIX] {fixed}개 해결, 남은 {len(missing)}개는 Fandom 다운로드 시도")

# 2단계: Fandom 다운로드
dl_ok = 0
for c in missing[:]:
    cid = c['id']
    base_en = c.get('base_en','')
    costume = c.get('costume','')
    print(f"[TRY DOWNLOAD] {cid} ({base_en} / {costume})")
    result = try_fandom_download(cid, base_en, costume)
    if result:
        c['image'] = BASE_URL + result
        dl_ok += 1
        missing.remove(c)

print(f"\n[DOWNLOAD] {dl_ok}개 다운로드 성공")
print(f"[REMAIN] {len(missing)}개 여전히 없음:")
for c in missing:
    print(f" - {c['id']}")

# 저장
CHAR_PATH.write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\n[DONE] {CHAR_PATH} 저장 완료")
print(f"그대로 두면 v2.0.7 PHP가 알아서 base 이미지로 보여주니까 사이트는 정상 작동함")
print(f"남은 {len(missing)}개는 수동으로 Fandom에서 받아서 {ASSET_DIR}/ 에 넣으면 끝")
