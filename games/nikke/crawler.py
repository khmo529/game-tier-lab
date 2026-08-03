import json, os, re, requests
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

DATA_DIR = Path("games/nikke/data")
CHAR_FILE = DATA_DIR / "characters.json"
WEEKLY_FILE = DATA_DIR / "weekly-update.json"
RAW_FILE = DATA_DIR / "prydwen_raw.json"
BASE_IMAGE_URL = "https://nopickle.co.kr/wp-content/themes/generatepress-child/nikke-tier/assets/images/"

# 전체 한글 매핑 216개 (수동 정리본 기준)
FULL_KO_MAP = {
    "Ada Wong":"에이다 웡","Anis: Star":"아니스: 스타","Crown":"크라운","Flora (Treasure)":"플로라(애장품)",
    "Vesti: Tactical Upgrade":"베스티: 택티컬 업그레이드","Moran (Treasure)":"모란(애장품)","Siren":"세이렌",
    "Mast: Romantic Maid":"마스트: 로맨틱 메이드","Nayuta":"나유타","Takina Inoue":"타키나 이노우에",
    "Cinderella: Crystal Wave":"신데렐라: 크리스탈 웨이브","Laplace: Ultimate Hero":"라플라스: 얼티밋 히어로",
    "Privaty (Treasure)":"프리바티(애장품)","Scarlet: Black Shadow":"홍련: 블랙 섀도우","Snow White: Heavy Arms":"스노우화이트: 헤비 암즈",
    "Red Hood B1":"레드후드 B1","Anchor: Innocent Maid":"앵커: 이노센트 메이드","Mint":"민트","Prika":"프리카","Alice":"앨리스",
    "Ein":"아인","Helm (Treasure)":"헬름(애장품)","Liberalio":"리베르타리오","Milk: Blooming Bunny":"밀크: 블루밍 버니",
    "Neon: Vision Eye":"네온: 비전 아이","Red Hood B3":"레드후드 B3","D: Killer Wife":"D: 킬러 와이프",
    "Emma: Tactical Upgrade":"엠마: 택티컬 업그레이드","Liter":"리터","Miranda (Treasure)":"미란다(애장품)","Rouge":"루주",
    "Soline: Frost Ticket":"솔린: 프로스트 티켓","Tia":"티아","Ade: Agent Bunny":"아데: 에이전트 버니","Blanc":"블랑",
    "Brid: Silent Track":"브리드: 사일런트 트랙","Eunhwa: Tactical Upgrade":"은화: 택티컬 업그레이드","Grave":"그레이브",
    "Mari Makinami Illustrious":"마리 마키나미 일러스트리어스","Naga":"나가","Velvet":"벨벳","Ark Ranger Black":"아크 레인저 블랙",
    "Asuka Shikinami Langley":"아스카 시키나미 랑그레이","Asuka Shikinami Langley: Wille":"아스카 시키나미 랑그레이: 빌레",
    "Cinderella":"신데렐라","Dorothy: Serendipity":"도로시: 세렌디피티","Maxwell":"맥스웰","Modernia":"모더니아",
    "Rei Ayanami":"레이 아야나미","Scarlet":"홍련","Anis: Sparkling Summer":"아니스: 스파클링 서머","Exia (Treasure)":"엑시아(애장품)",
    "Label":"라벨","Volume":"볼륨","Zwei (Treasure)":"츠바이(애장품)","Helm: Aquamarine":"헬름: 아쿠아마린","Crust":"크러스트",
    "Delta: Ninja Thief":"델타: 닌자 시프","Dolla":"달러","Rosanna: Chic Ocean":"로산나: 시크 오션","Trina":"트리나","Bready":"브레디",
    "Chisato Nishikigi":"치사토 니시키기","Diesel: Winter Sweets":"디젤: 윈터 스위츠","E.H.":"E.H.","Helm":"헬름",
    "Jill Valentine":"질 발렌타인","Laplace (Treasure)":"라플라스(애장품)","Ludmilla: Winter Owner":"루드밀라: 윈터 오너",
    "Maiden: Ice Rose":"메이든: 아이스 로즈","Noir":"누아르","Phantom":"팬텀","Privaty":"프라이버시",
    "Quency: Escape Queen":"퀀시: 이스케이프 퀸","Rei Ayanami (Tentative Name)":"레이 아야나미(가칭)","Snow White":"스노우화이트",
    "Alice: Wonderland Bunny":"앨리스: 원더랜드 버니","Mary: Bay Goddess":"메리: 베이 갓데스","Dorothy":"도로시",
    "Frima (Treasure)":"프리마(애장품)","Mica: Snow Buddy":"미카: 스노우 버디","Milk (Treasure)":"밀크(애장품)","Miranda":"미란다",
    "N102":"N102","Rapunzel":"라푼젤","Sakura":"사쿠라","Tove (Treasure)":"토브(애장품)","Zwei":"츠바이","Admi":"애드미","Anis":"아니스",
    "Arcana: Fortune Mate":"아르카나: 포츈 메이트","Centi":"센티","Centi (Treasure)":"센티(애장품)","Diesel (Treasure)":"디젤(애장품)",
    "Poli":"폴리","Poli (Treasure)":"폴리(애장품)","Rem":"렘","A2":"A2","Drake (Treasure)":"드레이크(애장품)","Emilia":"에밀리아","Eve":"이브",
    "Guillotine":"기요틴","Guillotine: Winter Slayer":"기요틴: 윈터 슬레이어","Harran":"하란","Snow White: Innocent Days":"스노우화이트: 이노센트 데이즈",
    "Mana":"마나","Marciana: Marine Study":"마르차나: 마린 스터디","Privaty: Unkind Maid":"프라이버시: 언카인드 메이드",
    "Soda: Twinkling Bunny":"소다: 트윙클링 버니","Avistar":"아비스타","Exia":"엑시아","Jackal":"자칼","Kurumi":"쿠루미","Ludmilla":"루드밀라",
    "Moran":"모란","Noise":"노이즈","Pepper":"페퍼","Rapunzel: Pure Grace":"라푼젤: 퓨어 그레이스","Rumani":"루마니","Sakura Suzuhara":"사쿠라 스즈하라",
    "Soda":"소다","Tove":"토브","Rupee: Winter Shopper":"루피: 윈터 쇼퍼","Yan":"얀","Ade":"아데","Arcana":"아르카나","Bay":"베이",
    "Bay (Treasure)":"베이(애장품)","Biscuit":"비스킷","Chime":"차임","Clay":"클레이","Elegg":"엘레그","Flora":"플로라","Makima":"마키마",
    "Marciana":"마르차나","Mast":"마스트","Anne: Miracle Fairy":"앤: 미라클 페어리","Noah":"노아","Quency":"퀀시","Rupee":"루피",
    "Snow Crane":"스노우 크레인","Viper (Treasure)":"바이퍼(애장품)","2B":"2B","Drake":"드레이크","Elegg: Boom and Shock":"엘레그: 붐 앤 쇼크",
    "Epinel":"에피넬","Julia (Treasure)":"줄리아(애장품)","Kilo":"킬로","Laplace":"라플라스","Raven":"레이븐","Sakura: Bloom in Summer":"사쿠라: 블룸 인 서머",
    "Vesti":"베스티","Anchor":"앵커","Claire Redfield":"클레어 레드필드","Cocoa":"코코아","Emma":"엠마","Ether":"에테르","Mary":"메리","Mica":"미카","Milk":"밀크",
    "Misato Katsuragi":"카츠라기 미사토","Neon":"네온","Pascal":"파스칼","Ram":"람","Rei":"레이","Rosanna":"로산나","Rosanna (Treasure)":"로산나(애장품)","Sora":"소라",
    "Aria":"아리아","Belorta":"벨로타","Delta":"델타","Diesel":"디젤","Eunhwa":"은화","Folkwang":"폴크방","Guilty":"길티","Himeno":"히메노","Leona":"레오나",
    "Lily":"릴리","Mori":"모리","Nero":"네로","Nihilister":"니힐리스터","Novel":"노벨","Red Hood B2":"레드후드 B2","Signal":"시그널","Sin":"신","Viper":"바이퍼","Yuni":"유니",
    "Neon: Blue Ocean":"네온: 블루 오션","Brid":"브리드","Crow":"크로우","Isabel":"이사벨","Julia":"줄리아","Maiden":"메이든","Mihara":"미하라",
    "Mihara: Bonding Chain":"미하라: 본딩 체인","Neve":"네베","Power":"파워","Quiry":"퀴리","Rapi":"라피","Soline":"솔린","Sugar":"슈가",
    "Trony":"트로니","Yulha":"율하","iDoll Flower":"아이돌 플라워","iDoll Ocean":"아이돌 오션","Product-08":"프로덕트 08","Soldier OW":"솔저 OW",
    "Product-23":"프로덕트 23","Soldier FA":"솔저 FA","iDoll Sun":"아이돌 선","Product-12":"프로덕트 12","Soldier EG":"솔저 EG",
    "Rapi RH":"라피 RH","Tabitha":"태버사","Red Hood":"레드후드","frima":"프리마"
}

TIER_ORDER = {"SSS":0,"SS":1,"S":2,"A":3,"B":4,"C":5}
PRYDWEN_MAP = {"SSS":"SSS","SS":"SS","S":"S","A":"A","B":"B","C":"C","D":"C","E":"C","F":"C"}

def to_image_filename(en_name: str) -> str:
    s = re.sub(r'[^A-Za-z0-9 ]',' ',en_name).strip()
    s = "_".join(s.split())
    return f"{BASE_IMAGE_URL}{s}.jpg"

def fetch_prydwen():
    headers={"User-Agent":"Mozilla/5.0"}
    try:
        r=requests.get("https://www.prydwen.gg/page-data/nikke/tier-list/page-data.json", headers=headers, timeout=20)
        if r.status_code==200:
            tiers={}
            def rec(o):
                if isinstance(o,dict):
                    if "name" in o and ("tier" in o or "rating" in o):
                        n=o.get("name"); t=o.get("tier") or o.get("rating")
                        if n and t and len(n)<50: tiers[n]=str(t).upper()
                    for v in o.values(): rec(v)
                elif isinstance(o,list):
                    for x in o: rec(x)
            rec(r.json())
            if tiers: return tiers
    except Exception as e:
        print(f"[WARN] page-data 실패 {e}")
    return {}

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    KST = ZoneInfo("Asia/Seoul")
    now_kst = datetime.now(KST)
    now_utc = datetime.now(timezone.utc)

    chars = json.load(open(CHAR_FILE, encoding="utf-8")) if CHAR_FILE.exists() else []
    trans_lower = {k.lower(): v for k,v in FULL_KO_MAP.items()}

    # 중복 제거 + 한글 강제

    # [FINAL FIX v2] 이름 최종 정리
    for c in list(dedup.values()):
        # 백설 -> 스노우화이트 (이미 위에서 치환됐지만 방어)
        if "백설" in c.get("name",""):
            c["name"] = c["name"].replace("백설", "스노우화이트")
        # 스칼렛 -> 홍련
        if c.get("name","").startswith("스칼렛"):
            c["name"] = c["name"].replace("스칼렛", "홍련")
        # 태버사 제거
        if c.get("name") == "태버사" or c.get("en_name","").lower() == "tabitha":
            del dedup[(c.get("en_name") or c.get("name") or "").lower()]
            continue
        # 레드후드 B1/B2/B3 통일
        if c.get("en_name") in ["Red Hood B1","Red Hood B2","Red Hood B3"]:
            c["name"] = "레드후드"
            c["image"] = f"{BASE_IMAGE_URL}Red_Hood.jpg"

    # 레드후드 중복 재제거
    dedup2 = {}
    for c in dedup.values():
        k = c["name"].lower()
        if k not in dedup2 or TIER_ORDER.get(c.get("tier","C"),99) < TIER_ORDER.get(dedup2[k].get("tier","C"),99):
            dedup2[k] = c
    dedup = dedup2

    dedup={}
    for c in sorted(chars, key=lambda x: (0 if x.get("company")!="미확인" else 1)):
        key=(c.get("en_name") or c.get("name") or "").lower()
        if not key: continue
        if key not in dedup:
            dedup[key]=c
        elif dedup[key].get("company")=="미확인" and c.get("company")!="미확인":
            dedup[key]=c

    cleaned=[]
    for c in dedup.values():
        en=c.get("en_name","")
        if en.lower() in trans_lower:
            c["name"]=trans_lower[en.lower()]
        c["image"]=to_image_filename(en or c["name"])
        cleaned.append(c)

    # prydwen 업데이트
    raw=fetch_prydwen()
    changed=[]
    for en_raw, tier_raw in raw.items():
        nt=PRYDWEN_MAP.get(tier_raw.upper())
        if not nt: continue
        key=en_raw.lower()
        if key in dedup:
            if dedup[key]["tier"]!=nt:
                changed.append({"name":dedup[key]["name"],"from":dedup[key]["tier"],"to":nt})
                dedup[key]["tier"]=nt

    # 저장
    final=list(dedup.values())
    final.sort(key=lambda x:(TIER_ORDER.get(x.get("tier","C"),99), x.get("name","")))
    with open(CHAR_FILE,"w",encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    weekly={
        "date": now_kst.strftime("%Y-%m-%d"),
        "week": f"{now_kst.strftime('%Y년 %m월 %d일')} 기준",
        "note": f"prydwen.gg Story 티어 기준 - {len(changed)}명 변동",
        "changes": changed,
        "total": len(final),
        "updated_at": now_utc.isoformat(),
        "updated_at_kst": now_kst.strftime("%Y-%m-%d %H:%M:%S KST")
    }
    with open(DATA_DIR / "weekly-update.json","w",encoding="utf-8") as f:
        json.dump(weekly, f, ensure_ascii=False, indent=2)

    print(f"DONE {len(final)}명 - {len(changed)}명 변동")

if __name__=="__main__":
    main()
