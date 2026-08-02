# Game Tier Lab - 니케 티어표 자동화

> prydwen.gg 기반 니케 티어리스트를 매주 자동으로 크롤링 → GitHub에 커밋 → 워드프레스로 자동 배포

## 🚀 동작 흐름
[prydwen.gg] --(크롤링)--> [crawler.py] --(병합)--> characters.json -> GitHub Auto Commit -> SFTP 워드프레스

- 매주 월요일 00:00 KST 자동 실행
- 수동 실행: Actions > Run workflow

## 📁 폴더 구조
game-tier-lab/
├── games/nikke/crawler.py
├── games/nikke/data/characters.json
├── games/nikke/data/weekly-update.json
├── games/nikke/data/prydwen_raw.json
└── .github/workflows/update.yml

## 🔧 crawler.py 로직
1. prydwen.gg /nikke/tier-list 에서 __NEXT_DATA__ 파싱
2. 영문명 -> 한글명 매핑 (Crown -> 크라운)
3. characters.json 병합 (tier, rating, history만 업데이트)
4. history 최대 8개 유지

## 🤖 GitHub Actions 최종본
name: 전체 티어표 자동 업데이트
on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * 1'
permissions:
  contents: write
jobs:
  update-nikke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: 니케 크롤러 실행
        run: |
          pip install requests beautifulsoup4 lxml
          python games/nikke/crawler.py
          ls -lh games/nikke/data/
      - name: 자동 커밋
        uses: stefanzweifel/git-auto-commit-action@v6
        with:
          commit_message: "auto: nikke update from prydwen"
          file_pattern: "games/nikke/data/*"
      - name: 워드프레스 배포
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.FTP_SERVER }}
          username: nopickle
          key: ${{ secrets.SSH_KEY }}
          port: 22
          source: "games/nikke/data/*"
          target: "/home/nopickle/htdocs/nopickle.co.kr/wp-content/themes/generatepress_child/nikke-tier/data/"
          strip_components: 3
          overwrite: true

## Secrets
- FTP_SERVER: Vultr IP
- SSH_KEY: private key

## 트러블슈팅
- characters.json 삭제시 자동 복구됨
- ssh unable to authenticate -> 키 인증만 가능 (CloudPanel)
- fetch first 에러 -> fetch-depth: 0
- 날짜 안바뀜 -> strip_components 3 확인, data/data 폴더 삭제