#!/usr/bin/env python3
# game/browndust2/tier_updater.py - 경로 고정 버전
import json
import os
from pathlib import Path
from datetime import datetime

# 스크립트 위치 기준 절대경로로 고정 (cwd가 어디든 동작)
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1] if (SCRIPT_DIR / "..").exists() else Path.cwd()

# 데이터 폴더 후보 (네 구조 대응)
CANDIDATES = [
    SCRIPT_DIR / "browndust2-tier" / "data",
    SCRIPT_DIR / "data",
    REPO_ROOT / "browndust2-tier" / "data",
    REPO_ROOT / "game" / "browndust2" / "browndust2-tier" / "data",
    Path.cwd() / "browndust2-tier" / "data",
    Path.cwd() / "game" / "browndust2" / "browndust2-tier" / "data",
]

def find_data_dir():
    for p in CANDIDATES:
        if p.exists():
            return p
    # 없으면 첫번째 후보에 생성
    first = CANDIDATES[0]
    first.mkdir(parents=True, exist_ok=True)
    return first

DATA_DIR = find_data_dir()
CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"

print(f"[BD2] SCRIPT_DIR={SCRIPT_DIR}")
print(f"[BD2] DATA_DIR={DATA_DIR}")
print(f"[BD2] CHAR_PATH={CHAR_PATH}")

def load_json(path, default):
    if not path.exists():
        print(f"[BD2] {path} not found, using default")
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    # 기존 데이터 로드
    characters = load_json(CHAR_PATH, [])
    weekly = load_json(WEEKLY_PATH, {})

    print(f"[BD2] Loaded {len(characters)} characters")

    # 여기서 실제 크롤링 로직이 들어가야 함 (Prydwen 등)
    # 지금은 기존 데이터 유지 + weekly 메타만 갱신
    # 예: characters.sort(key=...) 등 처리 가능

    # weekly 갱신
    now = datetime.now()
    github_run_id = os.environ.get("GITHUB_RUN_ID", "")
    github_sha = os.environ.get("GITHUB_SHA", "")

    # 기존 weekly 유지하면서 일부 필드만 갱신
    new_weekly = {
        "version": weekly.get("version") or now.strftime("%Y년 %m월 %W주차"),
        "updated": now.strftime("%Y-%m-%d"),
        "updated_at": now.isoformat(),
        "meta": weekly.get("meta", ""),
        "buff": weekly.get("buff", []),
        "nerf": weekly.get("nerf", []),
        "note": weekly.get("note", ""),
        "banner": weekly.get("banner", ""),
        "headline": weekly.get("headline", weekly.get("banner", "")),
        "deployed_at": now.isoformat(),
        "github_run_id": github_run_id,
        "github_sha": github_sha,
    }

    # 저장
    with open(CHAR_PATH, "w", encoding="utf-8") as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)
    print(f"[BD2] Saved {CHAR_PATH}")

    with open(WEEKLY_PATH, "w", encoding="utf-8") as f:
        json.dump(new_weekly, f, ensure_ascii=False, indent=2)
    print(f"[BD2] Saved {WEEKLY_PATH}")

if __name__ == "__main__":
    main()
