#!/usr/bin/env python3
# games/browndust2/tier_updater.py - games 경로 통합 + 빈 파일 대응
import json
import os
import shutil
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CHAR_PATH = DATA_DIR / "characters.json"
WEEKLY_PATH = DATA_DIR / "weekly-update.json"

print(f"[BD2] SCRIPT_DIR={SCRIPT_DIR}")
print(f"[BD2] DATA_DIR={DATA_DIR}")
print(f"[BD2] CHAR_PATH={CHAR_PATH} exists={CHAR_PATH.exists()} size={CHAR_PATH.stat().st_size if CHAR_PATH.exists() else 0}")

def load_json(path, default):
    if not path.exists():
        print(f"[BD2] {path} not found -> default 사용")
        return default
    try:
        if path.stat().st_size == 0:
            print(f"[BD2] {path} is empty -> default 사용")
            return default
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print(f"[BD2] {path} content empty -> default 사용")
                return default
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"[BD2] JSON 오류 {path}: {e} -> default 사용")
        # 백업
        try:
            backup = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup)
            print(f"[BD2] 손상된 파일 백업: {backup}")
        except:
            pass
        return default
    except Exception as e:
        print(f"[BD2] load 실패 {path}: {e} -> default 사용")
        return default

def main():
    characters = load_json(CHAR_PATH, [])
    weekly = load_json(WEEKLY_PATH, {})

    if not characters:
        print("[BD2] characters가 비어있음 - 기존 데이터가 없으면 빈 배열로 시작 (나중에 수동으로 채워야 함)")
    else:
        print(f"[BD2] Loaded {len(characters)} characters")

    now = datetime.now()
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
        "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "github_sha": os.environ.get("GITHUB_SHA", ""),
    }

    # 파일이 비었으면 일단 기본값이라도 저장해서 다음 실행 안터지게
    if not characters:
        # 임시로 빈 배열 저장 (너가 준 18개짜리는 아래에서 복구 가능)
        print("[BD2] 빈 파일이므로 빈 배열로 저장하고 넘어감 - characters.json을 다시 올려줘야 함")

    with open(CHAR_PATH, "w", encoding="utf-8") as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)
    print(f"[BD2] Saved {CHAR_PATH}")

    with open(WEEKLY_PATH, "w", encoding="utf-8") as f:
        json.dump(new_weekly, f, ensure_ascii=False, indent=2)
    print(f"[BD2] Saved {WEEKLY_PATH}")

    # 배포 폴더 동기화
    for deploy_parent in [SCRIPT_DIR / "browndust2-tier", Path.cwd() / "wordpress" / "browndust2-tier"]:
        if deploy_parent.exists() or deploy_parent.parent.exists():
            deploy_data = deploy_parent / "data"
            deploy_data.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(CHAR_PATH, deploy_data / "characters.json")
                shutil.copy2(WEEKLY_PATH, deploy_data / "weekly-update.json")
                print(f"[BD2] Copied to {deploy_data}")
            except Exception as e:
                print(f"[BD2] Copy fail {deploy_data}: {e}")

if __name__ == "__main__":
    main()
