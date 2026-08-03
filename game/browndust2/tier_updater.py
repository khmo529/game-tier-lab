import json, requests
from datetime import datetime

with open("browndust2-tier/data/characters.json","r",encoding="utf-8") as f:
    old = json.load(f)

# 여기서 prydwen.gg/page-data/brown-dust-2/tier-list/page-data.json 파싱
# 파싱 후 old와 비교해서 buff/nerf 리스트 생성

new_weekly = {
  "version": datetime.now().strftime("%Y년 %m월 %W주차"),
  "updated": datetime.now().strftime("%Y-%m-%d"),
  "updated_at": datetime.now().isoformat(),
  "buff": ["네브리스(사도 블레이드)","미카엘라(비치 저스티스)"],
  "nerf": [],
  "note": "GitHub Actions 자동 갱신",
  "banner": "신규 코스튬 반영",
  "github_run_id": "${{ github.run_id }}",
  "deployed_at": datetime.now().isoformat()
}
with open("browndust2-tier/data/weekly-update.json","w",encoding="utf-8") as f:
    json.dump(new_weekly,f,ensure_ascii=False,indent=2)
