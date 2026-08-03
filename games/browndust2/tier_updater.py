from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json

@dataclass
class CharacterTierItem:
    """캐릭터/코스튬 티어 정보를 담는 데이터 모델"""
    id: str
    name: str
    grade: str
    tier: str
    element: str
    attribute: str
    role: str
    type: str
    costume: str
    pve: float
    pvp: float
    guild: float
    boss: float
    image: str
    summary: str
    detail: str
    gear: List[str] = field(default_factory=list)
    team: List[str] = field(default_factory=list)
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    invest: int = 0
    beginner: bool = False
    updated_at: str = ""
    
    # 선택적 확장 필드 (일부 코스튬 항목 전용)
    name_en: Optional[str] = None
    base_en: Optional[str] = None
    base_ko: Optional[str] = None
    costume_ko: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterTierItem":
        """Dictionary 데이터로부터 객체를 안전하게 생성"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            grade=data.get("grade", ""),
            tier=data.get("tier", ""),
            element=data.get("element", "Unknown"),
            attribute=data.get("attribute", "Unknown"),
            role=data.get("role", "Unknown"),
            type=data.get("type", ""),
            costume=data.get("costume", ""),
            pve=float(data.get("pve", 0.0)),
            pvp=float(data.get("pvp", 0.0)),
            guild=float(data.get("guild", 0.0)),
            boss=float(data.get("boss", 0.0)),
            image=data.get("image", ""),
            summary=data.get("summary", ""),
            detail=data.get("detail", ""),
            gear=data.get("gear", []),
            team=data.get("team", []),
            pros=data.get("pros", []),
            cons=data.get("cons", []),
            invest=int(data.get("invest", 0)),
            beginner=bool(data.get("beginner", False)),
            updated_at=data.get("updatedAt", ""),
            name_en=data.get("name_en"),
            base_en=data.get("base_en"),
            base_ko=data.get("base_ko"),
            costume_ko=data.get("costume_ko")
        )

    def to_dict(self) -> Dict[str, Any]:
        """객체를 Dictionary 형태로 변환 (JSON 저장 시 활용)"""
        result = {
            "id": self.id,
            "name": self.name,
            "grade": self.grade,
            "tier": self.tier,
            "element": self.element,
            "attribute": self.attribute,
            "role": self.role,
            "type": self.type,
            "costume": self.costume,
            "pve": self.pve,
            "pvp": self.pvp,
            "guild": self.guild,
            "boss": self.boss,
            "image": self.image,
            "summary": self.summary,
            "detail": self.detail,
            "gear": self.gear,
            "team": self.team,
            "pros": self.pros,
            "cons": self.cons,
            "invest": self.invest,
            "beginner": self.beginner,
            "updatedAt": self.updated_at
        }
        # 선택적 필드가 존재하는 경우에만 포함
        if self.name_en: result["name_en"] = self.name_en
        if self.base_en: result["base_en"] = self.base_en
        if self.base_ko: result["base_ko"] = self.base_ko
        if self.costume_ko: result["costume_ko"] = self.costume_ko
        
        return result


class TierListManager:
    """티어 리스트 데이터를 관리하고 조회하는 클래스"""
    def __init__(self, raw_data: List[Dict[str, Any]] = None):
        self.items: List[CharacterTierItem] = []
        if raw_data:
            self.load_data(raw_data)

    def load_data(self, raw_data: List[Dict[str, Any]]):
        """raw JSON/Dict 데이터 파싱하여 내부 리스트 구축"""
        self.items = [CharacterTierItem.from_dict(item) for item in raw_data]

    def load_json_file(self, filepath: str):
        """JSON 파일로부터 데이터를 불러옴"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.load_data(data)

    def filter_by_grade(self, grade: str) -> List[CharacterTierItem]:
        """등급(SS+, SS, S, A 등)으로 필터링"""
        return [item for item in self.items if item.grade.upper() == grade.upper()]

    def filter_by_element(self, element: str) -> List[CharacterTierItem]:
        """속성(Wind, Dark, Light, Fire, Water 등)으로 필터링"""
        return [item for item in self.items if item.element.lower() == element.lower()]

    def get_beginner_recommended(self) -> List[CharacterTierItem]:
        """초보자 추천 캐릭터 목록 추출"""
        return [item for item in self.items if item.beginner]

    def get_top_pve(self, limit: int = 5) -> List[CharacterTierItem]:
        """PVE 상위 캐릭터 목록 추출"""
        return sorted(self.items, key=lambda x: x.pve, reverse=True)[:limit]

    def search_by_name(self, keyword: str) -> List[CharacterTierItem]:
        """이름 키워드 검색 (한국어 및 영어 대응)"""
        keyword_lower = keyword.lower()
        results = []
        for item in self.items:
            if keyword_lower in item.name.lower():
                results.append(item)
            elif item.name_en and keyword_lower in item.name_en.lower():
                results.append(item)
            elif item.base_ko and keyword_lower in item.base_ko.lower():
                results.append(item)
        return results


# --- 간단 사용 예시 ---
if __name__ == "__main__":
    # 제공받은 JSON 데이터 예시 입력
    sample_json = [
        {
            "id": "diana",
            "name": "디아나",
            "grade": "SS+",
            "tier": "SS+",
            "element": "Wind",
            "role": "Support",
            "pve": 10.0,
            "pvp": 8.5,
            "beginner": True
        },
        {
            "id": "morpeah-apostle",
            "name": "모르페아 (사도)",
            "name_en": "Morpeah: Apostle",
            "base_ko": "모르페아",
            "grade": "S",
            "tier": "S",
            "element": "Unknown",
            "pve": 8.0,
            "pvp": 8.0,
            "beginner": False
        }
    ]

    # 매니저 클래스 생성 및 데이터 로드
    manager = TierListManager(sample_json)

    # 1. PVE 상위 캐릭터 조회
    top_pve = manager.get_top_pve(1)
    print(f"Top PVE 캐릭터: {top_pve[0].name} (점수: {top_pve[0].pve})")

    # 2. 이름 검색 테스트
    search_result = manager.search_by_name("모르페아")
    print(f"검색 결과: {[item.name for item in search_result]}")
