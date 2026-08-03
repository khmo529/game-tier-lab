#!/usr/bin/env python3
# game/browndust2/tier_updater.py - 생성 경로: game/browndust2/data 고정
import json
import os
import shutil
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"  # 요청한 경로: game/browndust2/data
DEPLOY_CANDIDATES = [
    SCRIPT_DIR / "browndust2-tier" / "data",
    SCRIPT_DIR.parent / "wordpress" / "browndust2-tier" / "data",
    Path.cwd() / "wordpress" / "browndust2-tier" / "data",
    Path.cwd() / "browndust2-tier" / "data",
]

DATA_DIR.mkdir(parents=True, exist_ok=True)

CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"

print(f"[BD2] SCRIPT_DIR={SCRIPT_DIR}")
print(f"[BD2] DATA_DIR={DATA_DIR} (생성 위치)")
print(f"[BD2] CHAR_PATH={CHAR_PATH}")

def load_json(path, default):
    if not path.exists():
        print(f"[BD2] {path} not found, using default")
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    characters = load_json(CHAR_PATH, [])
    weekly = load_json(WEEKLY_PATH, {})

    print(f"[BD2] Loaded {len(characters)} characters from {CHAR_PATH}")

    now = datetime.now()
    github_run_id = os.environ.get("GITHUB_RUN_ID", "")
    github_sha = os.environ.get("GITHUB_SHA", "")

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

    with open(CHAR_PATH, "w", encoding="utf-8") as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)
    print(f"[BD2] Saved {CHAR_PATH}")

    with open(WEEKLY_PATH, "w", encoding="utf-8") as f:
        json.dump(new_weekly, f, ensure_ascii=False, indent=2)
    print(f"[BD2] Saved {WEEKLY_PATH}")

    # 배포용 폴더에도 자동 복사 (있으면)
    for deploy_data_dir in DEPLOY_CANDIDATES:
        if deploy_data_dir.parent.exists():
            deploy_data_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(CHAR_PATH, deploy_data_dir / "characters.json")
                shutil.copy2(WEEKLY_PATH, deploy_data_dir / "weekly-update.json")
                print(f"[BD2] Copied to deploy dir: {deploy_data_dir}")
            except Exception as e:
                print(f"[BD2] Copy failed to {deploy_data_dir}: {e}")

if __name__ == "__main__":
    main()
