"""Original compatibility heuristic for the Star & Moon diagnosis v1.6.

The score is an entertainment/self-reflection device, not a validated measure
of relationship success. It deliberately exposes its simple scoring rules.
"""
from dataclasses import dataclass
from independent_12_animal_diagnosis_v1_3 import CHARACTERS, diagnose as diagnose_character
from love_type_16_v1_4 import TYPES, LoveType

CHAR_BY_ID = {c.id: c for c in CHARACTERS}
# Fictional five-element affinity table designed for this original product.
# Values are symmetric, 0..20; not presented as traditional fortune-telling fact.
ELEMENT_AFFINITY = {
    frozenset(("木", "木")): 15,
    frozenset(("火", "火")): 15,
    frozenset(("土", "土")): 15,
    frozenset(("金", "金")): 15,
    frozenset(("水", "水")): 15,
    frozenset(("木", "火")): 19,
    frozenset(("火", "土")): 19,
    frozenset(("土", "金")): 19,
    frozenset(("金", "水")): 19,
    frozenset(("水", "木")): 19,
    frozenset(("木", "土")): 7,
    frozenset(("火", "水")): 7,
    frozenset(("金", "木")): 7,
    frozenset(("土", "水")): 10,
    frozenset(("金", "火")): 10,
}
AXIS_LABELS = ("距離の縮め方", "愛情の伝え方", "恋のペース", "心地よい距離")

@dataclass(frozen=True)
class PersonProfile:
    label: str
    birth_date: str
    character_id: str
    character_name: str
    element: str
    keywords: tuple[str, ...]
    love_code: str
    love_name: str
    love_tagline: str
    love_strengths: tuple[str, ...]
    love_blind_spots: tuple[str, ...]
    love_advice: str
    calendar_warnings: tuple[str, ...] = ()

@dataclass(frozen=True)
class CompatibilityResult:
    score: int
    level: str
    character_score: int
    love_type_score: int
    shared_axes: tuple[str, ...]
    different_axes: tuple[str, ...]
    attraction_points: tuple[str, ...]
    friction_points: tuple[str, ...]
    advice: tuple[str, ...]
    explanation: str


def make_profile(label: str, birth_date: str, love_code: str, birth_time: str | None = None) -> PersonProfile:
    if love_code not in TYPES:
        raise ValueError(f"{label}の恋愛タイプを選択してください")
    animal = diagnose_character(birth_date, birth_time)
    love = TYPES[love_code]
    return PersonProfile(
        label=label, birth_date=birth_date,
        character_id=animal.character_id, character_name=animal.character_name,
        element=animal.element, keywords=animal.keywords, calendar_warnings=animal.warnings,
        love_code=love.code, love_name=love.name, love_tagline=love.tagline,
        love_strengths=love.strengths, love_blind_spots=love.blind_spots,
        love_advice=love.advice,
    )


def _code_axes(code: str) -> tuple[str, ...]:
    if code not in TYPES:
        raise ValueError(f"不正な恋愛タイプコード: {code}")
    return tuple(code)


def calculate_compatibility(a: PersonProfile, b: PersonProfile) -> CompatibilityResult:
    ca, cb = CHAR_BY_ID[a.character_id], CHAR_BY_ID[b.character_id]
    affinity = ELEMENT_AFFINITY.get(frozenset((a.element, b.element)), 12)
    # Convert 0..20 element affinity to 0..100. The result is a transparent
    # project-specific score, not a prediction of relationship outcome.
    character_score = round(affinity / 20 * 100)

    bits_a, bits_b = _code_axes(a.love_code), _code_axes(b.love_code)
    shared_indices = [i for i, (x, y) in enumerate(zip(bits_a, bits_b)) if x == y]
    different_indices = [i for i, (x, y) in enumerate(zip(bits_a, bits_b)) if x != y]
    # Similarity scores are 40..100: 40 + 15 per matching axis.
    love_type_score = 40 + 15 * len(shared_indices)
    # Overall weight: 35% character affinity + 65% love-style similarity.
    score = round(character_score * 0.35 + love_type_score * 0.65)
    level = "とても噛み合いやすい" if score >= 85 else "理解を深めやすい" if score >= 70 else "違いを知ると伸びる" if score >= 55 else "丁寧なすり合わせが鍵"

    shared_axes = tuple(AXIS_LABELS[i] for i in shared_indices)
    different_axes = tuple(AXIS_LABELS[i] for i in different_indices)
    attraction = []
    friction = []
    advice = []
    if "距離の縮め方" in shared_axes:
        attraction.append("関係を進めるテンポが近く、誘い方や待ち方を理解しやすい")
    else:
        friction.append("一方は先に動き、もう一方は様子を見るなど、進展の速度に差が出ることがある")
        advice.append("誘う側・待つ側を固定せず、相手が心地よいペースを言葉で確認する")
    if "愛情の伝え方" in shared_axes:
        attraction.append("愛情表現の受け取り方が近く、気持ちが伝わりやすい")
    else:
        friction.append("言葉と行動のどちらを愛情として受け取りやすいかが異なる可能性がある")
        advice.append("『言葉で伝えてほしい』『行動で示してくれるとうれしい』を具体的に共有する")
    if "恋のペース" in shared_axes:
        attraction.append("安定と刺激のどちらを重視するかが近い")
    else:
        friction.append("落ち着いた日常と新しい体験のバランスに違いが出やすい")
        advice.append("定番の予定と新しい体験を交互に取り入れ、双方の希望を反映する")
    if "心地よい距離" in shared_axes:
        attraction.append("一緒に過ごす時間と個人の時間について感覚を合わせやすい")
    else:
        friction.append("連絡頻度や一人の時間への希望が違うことがある")
        advice.append("連絡の目安や一人時間を先に相談し、距離を愛情の強さと決めつけない")

    if a.element == b.element:
        attraction.append(f"同じ五行グループ（{a.element}）として、似た価値観を感じるという読み方ができる")
    elif affinity >= 19:
        attraction.append(f"五行カラーの組み合わせ（{a.element}×{b.element}）を、互いの良さを引き出す象徴として扱う")
    elif affinity <= 7:
        friction.append(f"五行カラー（{a.element}×{b.element}）の違いを、優劣ではなく考え方の違いとして話し合う")
        advice.append("意見が分かれたら、どちらが正しいかより『何を大切にしているか』を確認する")

    if not advice:
        advice.append("相性が良いと感じても、希望や境界線は確認し合い、小さな約束を積み重ねる")
    if not friction:
        friction.append("傾向が似ている場合も、言わなくても分かると決めつけず、希望を言葉にする")
    explanation = (f"恋愛タイプは4軸中{len(shared_indices)}軸が一致。キャラクターの五行 affinity を含む独自ルールで算出した参考スコアです。")
    return CompatibilityResult(
        score=max(0, min(100, score)), level=level,
        character_score=character_score, love_type_score=love_type_score,
        shared_axes=shared_axes, different_axes=different_axes,
        attraction_points=tuple(attraction[:4]), friction_points=tuple(friction[:4]),
        advice=tuple(dict.fromkeys(advice))[:4], explanation=explanation,
    )


def self_test() -> str:
    assert len(CHAR_BY_ID) == 12 and len(TYPES) == 16
    # Test all 192 x 192 combinations of character and love type, represented
    # by deterministic sample profiles; all results must stay in 0..100.
    profiles = []
    for c in CHARACTERS:
        for code, love in TYPES.items():
            profiles.append(PersonProfile("test", "2000-01-01", c.id, c.name, c.element,
                c.keywords, code, love.name, love.tagline, love.strengths,
                love.blind_spots, love.advice))
    for p in profiles:
        r = calculate_compatibility(p, p)
        assert 0 <= r.score <= 100 and r.shared_axes == AXIS_LABELS
    for a in profiles:
        for b in profiles:
            r = calculate_compatibility(a, b)
            assert 0 <= r.score <= 100
            assert len(r.shared_axes) + len(r.different_axes) == 4
    return f"OK: {len(profiles)} profiles; {len(profiles)**2:,} pair combinations; score range and axis coverage valid."

if __name__ == "__main__":
    print(self_test())
