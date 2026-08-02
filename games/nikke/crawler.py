import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

print("NIKKE 크롤러 시작")

# 한국 시간으로 고정
now = datetime.now(ZoneInfo("Asia/Seoul"))

DATA_DIR = "games/nikke/data"
os.makedirs(DATA_DIR, exist_ok=True)

char_path = f"{DATA_DIR}/characters.json"
weekly_path = f"{DATA_DIR}/weekly-update.json"

# weekly-update.json 생성/업데이트
weekly = {
    "version": f"{now:%Y}-W{now.isocalendar()[1]}",
    "updated_at": now.strftime("%Y-%m-%d %H:%M KST"),
    "headline": f"{now.month}월 {now.day}일 자동 업데이트 성공!",
    "changes": [],
    "notice": "game-tier-lab에서 자동 갱신됨"
}

with open(weekly_path, 'w', encoding='utf-8') as f:
    json.dump(weekly, f, ensure_ascii=False, indent=2)

# characters.json이 없으면 샘플 생성
if not os.path.exists(char_path):
    sample = [{"id": "scarlet", "name": "스칼렛", "tier": "S"}]
    with open(char_path, 'w', encoding='utf-8') as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)

print(f"완료: {weekly['updated_at']}")
