# Game Tier Lab - NIKKE Tier Auto Update

> prydwen.gg 기반 티어리스트를 매주 자동 크롤링 → GitHub 커밋 → 워드프레스 자동 배포

## Overview
- 매주 월요일 00:00 UTC 자동 실행 (cron)
- 수동 실행: GitHub Actions > Run workflow
- prydwen.gg 티어 변동 시 history 자동 누적

## Folder Structure
game-tier-lab/
├── games/nikke/
│   ├── crawler.py
│   └── data/
│       ├── characters.json
│       ├── weekly-update.json
│       └── prydwen_raw.json
└── .github/workflows/update.yml

## How Crawler Works
1. Fetch https://www.prydwen.gg/nikke/tier-list
2. Parse __NEXT_DATA__ JSON (Next.js)
3. Map EN name to KO name via table
4. Merge into characters.json (only tier/rating/history)
5. Generate weekly-update.json changelog

## GitHub Actions Workflow
name: Update Tier
on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * 1'
permissions:
  contents: write
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run crawler
        run: |
          pip install requests beautifulsoup4 lxml
          python games/nikke/crawler.py
      - name: Auto commit
        uses: stefanzweifel/git-auto-commit-action@v6
        with:
          commit_message: "auto: tier update"
          file_pattern: "games/nikke/data/*"
      - name: Deploy via SFTP
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.FTP_SERVER }}
          username: ${{ secrets.FTP_USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          port: 22
          source: "games/nikke/data/*"
          target: ${{ secrets.DEPLOY_PATH }}
          strip_components: 3
          overwrite: true

### Required Secrets
- FTP_SERVER
- FTP_USERNAME
- SSH_KEY
- DEPLOY_PATH

## Troubleshooting
- Deleted characters.json not restored -> new crawler auto-restores
- ssh unable to authenticate -> use key auth
- fetch first error -> fetch-depth: 0
- Date not updated -> strip_components 3 확인