#!/usr/bin/env python3
# tier_updater v15 - 티어 변경은 반영하되 이미지는 절대 안 건드리는 최신화 버전
# - 등급(grade), 점수(pve/pvp/guild/boss)만 외부에서 가져와 업데이트
# - image, element, role, costume, base_en 등 절대 덮어쓰지 않음
# - 새 캐릭터가 생기면 slug.png 형식으로 추가 (이미지 없으면 justia.png 임시)

import json, re, os, requests
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"

KST = ZoneInfo("Asia/Seoul")

def load_json(path, default):
    if not path.exists(): return default
    try: return json.loads(path.read_text(encoding='utf-8'))
    except: return default

def fetch_tiers_pocket_tactics():
    """Pocket Tactics에서 티어 크롤링 시도 - 실패하면 빈 dict 반환"""
    url = "https://www.pockettactics.com/brown-dust-2/tier-list"
    tiers = {}
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code==200:
            text = r.text
            # 간단 파싱: SS+, SS, S, A, B, C 섹션에서 캐릭터 이름 추출
            # 실제 사이트 구조에 따라 정규식 조정 필요
            # 예시: <h3>SS+ Tier</h3> ... <li>Justia - Knight of Blood</li>
            for tier in ["SS\+", "SS", "S", "A", "B", "C"]:
                pattern = rf'{tier} Tier.*?</h3>.*?<ul>(.*?)</ul>'
                m = re.search(pattern, text, re.I | re.S)
                if m:
                    # 이름 추출
                    names = re.findall(r'<li>(.*?)</li>', m.group(1), re.S)
                    tiers[tier.replace("\\","")] = [re.sub(r'<.*?>','',n).strip() for n in names]
        print(f"[FETCH] Pocket Tactics tiers: { {k:len(v) for k,v in tiers.items()} }")
    except Exception as e:
        print(f"[FETCH FAIL] {e}")
    return tiers

def fetch_tiers_fallback():
    """외부 크롤링 실패시 사용할 기본 등급 (기존 파일 유지)"""
    return {}

def normalize_name(s):
    return re.sub(r'[^a-z0-9]','',s.lower()) if s else ""

def slugify(s):
    s=s.lower()
    s=re.sub(r'[^a-z0-9]+','-',s)
    return re.sub(r'^-+|-+$','',s)

def main():
    chars = load_json(CHAR_PATH, [])
    if not chars:
        print("[ERROR] characters.json 없음 - 먼저 characters_final_167_CLEAN.json을 characters.json으로 복구하세요")
        return

    print(f"[BD2 v15] 기존 캐릭터 {len(chars)}개 로드")

    # 1. 외부 티어 가져오기
    external_tiers = fetch_tiers_pocket_tactics()
    if not external_tiers:
        external_tiers = fetch_tiers_fallback()
        print("[INFO] 외부 티어 가져오기 실패 - 기존 등급 유지하고 weekly만 갱신")

    # 2. 등급 매핑 테이블 만들기: 캐릭터 이름 -> 등급
    # Pocket Tactics 이름은 "Justia - Knight of Blood" 형식일 수 있음
    name_to_grade = {}
    for tier, names in external_tiers.items():
        for name in names:
            # "Justia - Knight of Blood" -> base_en=Justia, costume=Knight of Blood
            if " - " in name:
                base, costume = name.split(" - ",1)
                sid = slugify(f"{base} {costume}")
                name_to_grade[sid] = tier
                name_to_grade[normalize_name(name)] = tier
            else:
                name_to_grade[normalize_name(name)] = tier

    # 3. 기존 캐릭터 등급만 업데이트 (이미지는 절대 안 건드림!)
    updated_count = 0
    for c in chars:
        cid = c['id']
        # 외부에서 등급 찾았으면 업데이트, 못 찾았으면 기존 유지
        new_grade = name_to_grade.get(cid) or name_to_grade.get(normalize_name(c.get('name_en','')+c.get('costume','')))
        if new_grade and new_grade != c.get('grade'):
            print(f"  [GRADE UPDATE] {cid}: {c.get('grade')} -> {new_grade}")
            c['grade'] = new_grade
            c['tier'] = new_grade
            updated_count += 1
        # 점수는 외부에서 안 가져오면 기존 유지 (원하면 여기서 pve/pvp도 업데이트)
        # 이미지, element, role, base_en, costume 등은 절대 덮어쓰지 않음!

    # 4. 새 캐릭터가 있으면 추가 (이미지는 slug.png)
    # external_tiers에 있는데 기존에 없는 캐릭터
    existing_ids = set(c['id'] for c in chars)
    for tier, names in external_tiers.items():
        for name in names:
            if " - " in name:
                base, costume = name.split(" - ",1)
                sid = slugify(f"{base} {costume}")
                if sid not in existing_ids:
                    print(f"  [NEW CHAR] {sid} ({tier}) 추가")
                    chars.append({
                        "id": sid,
                        "name": f"{base} ({costume})",
                        "name_en": base,
                        "base_en": base,
                        "base_ko": base,
                        "costume": costume,
                        "costume_ko": costume,
                        "grade": tier,
                        "tier": tier,
                        "element": "Unknown",
                        "role": "Unknown",
                        "type": "Standard",
                        "pve": 8.0, "pvp": 8.0, "guild": 8.0, "boss": 8.0, "score": 8.0,
                        "image": f"https://nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/assets/images/{sid}.png",
                        "summary": f"{base} ({costume}) - {tier}티어",
                        "detail": "", "gear": [], "team": [], "pros": [], "cons": [], "invest": 3, "beginner": False
                    })
                    existing_ids.add(sid)

    # 5. 저장 (이미지 보존됨)
    CHAR_PATH.write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[BD2] characters.json 저장: {len(chars)}개, 등급 변경 {updated_count}개 (이미지 유지)")

    # 6. weekly 갱신 - 실제 등급 기준으로 집계 (S:0 버그 해결)
    counter = Counter(c.get('grade') or 'C' for c in chars)
    now = datetime.now(KST)
    meta = "전체 %d개 / " % len(chars) + " ".join(f"{t}:{counter[t]}" for t in ['SS+','SS','S','A','B','C'] if t in counter)
    weekly = load_json(WEEKLY_PATH, {})
    weekly.update({
        "version": f"{now.year}년 {now.month:02d}월 {(now.day-1)//7+1}주차 (W{now.isocalendar()[1]})",
        "updated": now.strftime("%Y-%m-%d"),
        "updated_at": now.isoformat(),
        "deployed_at": now.isoformat(),
        "meta": meta,
        "total": len(chars),
        "grades": dict(counter),
    })
    WEEKLY_PATH.write_text(json.dumps(weekly, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[BD2] weekly: {meta}")
    print("[BD2 v15] 완료! 티어는 최신화됐고 이미지는 그대로 유지됩니다.")

if __name__ == "__main__":
    main()
