#!/usr/bin/env python3
# games/browndust2/tier_updater.py - v11 SAFE: characters.json 절대 안 건드림, weekly 등급만 실제 집계
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"

KST = ZoneInfo("Asia/Seoul")
now_kst = datetime.now(KST)

def load_json(path, default):
    if not path.exists(): return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except: return default

def main():
    chars = load_json(CHAR_PATH, [])
    if not chars:
        print("[BD2] characters.json 없음 - 종료")
        return
    counter = Counter(c.get("grade") or c.get("tier") or "C" for c in chars)
    print(f"[BD2] 등급 분포: {dict(counter)}")

    weekly = load_json(WEEKLY_PATH, {})
    iso_week = now_kst.isocalendar()[1]
    wom = (now_kst.day-1)//7+1
    order = ["SS+","SS","S","A","B","C"]
    meta_parts = [f"{t}:{counter[t]}" for t in order if t in counter]
    meta_str = f"전체 {len(chars)}개 / " + " ".join(meta_parts) if meta_parts else f"전체 {len(chars)}개"

    new_weekly = {
        **weekly,
        "version": f"{now_kst.year}년 {now_kst.month:02d}월 {wom}주차 (W{iso_week})",
        "updated": now_kst.strftime("%Y-%m-%d"),
        "updated_at": now_kst.isoformat(),
        "deployed_at": now_kst.isoformat(),
        "meta": meta_str,
        "total": len(chars),
        "grades": dict(counter),
    }
    WEEKLY_PATH.write_text(json.dumps(new_weekly, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[BD2] weekly 수정 완료: {meta_str} - characters.json은 건드리지 않음")

if __name__ == "__main__":
    main()
