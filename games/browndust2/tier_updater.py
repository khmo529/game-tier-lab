#!/usr/bin/env python3
# games/browndust2/tier_updater.py - v4: KST 고정 + characters.json 보존
import json
import os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"

KST = ZoneInfo("Asia/Seoul")
now_kst = datetime.now(KST)

print(f"[BD2] KST now: {now_kst.isoformat()}")
print(f"[BD2] CHAR_PATH={CHAR_PATH} exists={CHAR_PATH.exists()}")

def load_json(path, default):
    if not path.exists():
        return default
    try:
        if path.stat().st_size == 0:
            return default
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except Exception as e:
        print(f"[BD2] load fail {path}: {e}")
        return default

def main():
    characters = load_json(CHAR_PATH, None)
    weekly = load_json(WEEKLY_PATH, {})

    # characters.json은 절대 덮어쓰지 않음 - 없으면 에러로 알림만
    if characters is None:
        print(f"[BD2][ERROR] {CHAR_PATH}가 없습니다! 수동으로 복구해야 합니다.")
        # 빈 배열로 생성하지 않고 종료해서 데이터 날라가는 것 방지
        return
    else:
        print(f"[BD2] characters.json 보존 - {len(characters)}개 유지 (덮어쓰기 안함)")

    # weekly-update.json만 KST 기준으로 업데이트
    # version은 ISO 주차 기준으로 생성: 2026년 08월 32주차 형태
    iso_year, iso_week, iso_day = now_kst.isocalendar()
    # 월 주차 계산 (1~5주차)
    week_of_month = (now_kst.day - 1) // 7 + 1

    # 기존 weekly 값은 최대한 보존하고 시간만 갱신
    new_weekly = {
        **weekly,  # 기존 buff/nerf/meta/banner 등 유지
        "version": f"{now_kst.year}년 {now_kst.month:02d}월 {week_of_month}주차 (W{iso_week})",
        "updated": now_kst.strftime("%Y-%m-%d"),
        "updated_at": now_kst.isoformat(),  # KST +09:00 포함
        "deployed_at": now_kst.isoformat(),
        "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "github_sha": os.environ.get("GITHUB_SHA", ""),
    }

    # 빈 필드 기본값 보정
    new_weekly.setdefault("meta", "")
    new_weekly.setdefault("buff", [])
    new_weekly.setdefault("nerf", [])
    new_weekly.setdefault("note", "")
    new_weekly.setdefault("banner", "")
    new_weekly.setdefault("headline", new_weekly.get("banner", ""))

    with open(WEEKLY_PATH, "w", encoding="utf-8") as f:
        json.dump(new_weekly, f, ensure_ascii=False, indent=2)
    print(f"[BD2] Saved WEEKLY: {WEEKLY_PATH}")
    print(json.dumps(new_weekly, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
