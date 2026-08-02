import json, os
from datetime import datetime
import requests

# 1. 데이터 가져오기 (지금은 Prydwen 테스트)
# 실제 파싱은 나중에 고도화하고, 지금은 updated_at만 갱신해서 배포 테스트
print("NIKKE 크롤러 시작")

DATA_DIR = "games/nikke/data"
os.makedirs(DATA_DIR, exist_ok=True)

# 기존 파일이 없으면 새로 만듦
char_path = f"{DATA_DIR}/characters.json"
weekly_path = f"{DATA_DIR}/weekly-update.json"

# weekly-update.json 생성/업데이트
weekly = {
    "version": f"{datetime.now():%Y}-W{datetime.now().isocalendar()[1]}",
    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "headline": f"{datetime.now().month}월 {datetime.now().day}일 자동 업데이트 성공!",
    "changes": [],
    "notice": "game-tier-lab에서 자동 갱신됨"
}

with open(weekly_path, 'w', encoding='utf-8') as f:
    json.dump(weekly, f, ensure_ascii=False, indent=2)

# characters.json이 없으면 샘플 생성
if not os.path.exists(char_path):
    sample = [{"id":"scarlet","name":"스칼렛","tier":"S"}]
    with open(char_path, 'w', encoding='utf-8') as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)

print("완료")
