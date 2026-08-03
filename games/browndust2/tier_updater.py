#!/usr/bin/env python3
# tier_updater v15.2 - GitHub Action + Vultr 둘 다 되는 경로 고정 버전
import json, re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter

# === 경로 고정: 이 파일 위치 기준으로 절대경로 사용 ===
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"

# Vultr(CloudPanel)에서도 돌아가게 대체 경로 탐색
if not CHAR_PATH.exists():
    alt_paths = [
        Path("/home/nopickle/htdocs/nopickle.co.kr/wp-content/themes/generatepress-child/browndust2-tier/data/characters.json"),
        Path.cwd() / "games/browndust2/data/characters.json",
        Path.cwd() / "data/characters.json",
    ]
    for p in alt_paths:
        if p.exists():
            CHAR_PATH = p
            DATA_DIR = p.parent
            WEEKLY_PATH = DATA_DIR / "weekly-update.json"
            break

KST = ZoneInfo("Asia/Seoul")

def load_json(path, default):
    if not path.exists():
        print(f"[WARN] {path} 없음, 기본값 사용")
        return default
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"[WARN] {path} 로드 실패: {e}")
        return default

def slugify(s):
    s=s.lower()
    s=re.sub(r'[^a-z0-9]+','-',s)
    return re.sub(r'^-+|-+$','',s)

def normalize_name(s):
    return re.sub(r'[^a-z0-9]','',s.lower()) if s else ""

def main():
    print(f"[PATH] SCRIPT_DIR={SCRIPT_DIR}")
    print(f"[PATH] DATA_DIR={DATA_DIR}")
    print(f"[PATH] CHAR_PATH={CHAR_PATH}")
    print(f"[PATH] exists={CHAR_PATH.exists()}")

    chars = load_json(CHAR_PATH, [])
    if not chars:
        print(f"[ERROR] {CHAR_PATH} 비어있음 - 복구 필요")
        # 빈 파일이면 생성하지 말고 종료
        return

    print(f"[BD2 v15.2] 캐릭터 {len(chars)}개 로드")

    # 외부 크롤링은 일단 스킵 (Pocket Tactics 파싱 불안정) - 등급은 기존 유지
    # 필요하면 나중에 fetch 로직 추가

    # weekly 집계
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
    CHAR_PATH.write_text(json.dumps(chars, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[BD2] 저장 완료: {len(chars)}개, {meta}")

if __name__ == "__main__":
    main()
