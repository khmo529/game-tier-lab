[prydwen.gg] --(크롤링)--> [crawler.py] --(병합)--> characters.json
      ↓                                              ↓
prydwen_raw.json / weekly-update.json         [GitHub Auto Commit]
                                                     ↓
                                           [SFTP] 워드프레스 테마 폴더
                                           /wp-content/themes/.../nikke-tier/data/
game-tier-lab/
├── games/
│   └── nikke/
│       ├── crawler.py
│       └── data/
│           ├── characters.json
│           ├── weekly-update.json
│           ├── prydwen_raw.json
│           └── .gitkeep
└── .github/
    └── workflows/
        └── update.yml
### 2. 한글 <-> 영문 매핑
### 3. characters.json 병합
- 파일 없으면 prydwen 데이터로 자동 재생성
- 있으면 티어 다른 애만 업데이트
    - `history`에 이전 티어 추가 (최대 8개)
    - `rating` 자동 보정 (SSS=5, S=4, A=3...)
    - `pros/cons/team` 같은 수동 데이터는 유지

## 🤖 GitHub Actions (update.yml)
### 필수 Secrets
- `FTP_SERVER` : Vultr 서버 IP
- `SSH_KEY` : `nopickle` 유저 private key

## 🌐 워드프레스 연동
## 💡 더 나은 구조 제안
## ❓ 트러블슈팅

**Q. characters.json 지웠는데 안 생겨요**
A. 새 크롤러는 자동 복구됨. `python games/nikke/crawler.py` 실행.

**Q. ssh: unable to authenticate**
A. CloudPanel은 패스워드 로그인 차단. 키 인증만 가능.

**Q. main -> main (fetch first)**
A. checkout에 `fetch-depth: 0` 추가.

**Q. 워드프레스 날짜 안 바뀌어요**
A. `strip_components: 3` 확인. `2`면 `data/data/`에 들어감.
`rm -rf .../nikke-tier/data/data/` 로 삭제.

---
Made by nopickle.co.kr
