"""Independent 12-character diagnosis v1.3.

Calculates year/month/day pillars from a Gregorian birth date in Japan Standard
Time (JST), then maps them to the original 12-character taxonomy.

Important:
- Original character mapping and scoring are product-design heuristics, not
  traditional or scientifically validated personality predictions.
- Solar terms are calculated with pyswisseph when available.
- Day pillar switches at local midnight as specified by the project.
- Birth time is optional; without it, noon JST is used for solar-term placement
  while the day pillar always follows the entered calendar date.
"""
from dataclasses import dataclass, asdict
from datetime import date, datetime, time, timedelta, timezone
from itertools import product
from zoneinfo import ZoneInfo
import math
import json
from pathlib import Path
from functools import lru_cache

try:
    import swisseph as swe
except ImportError:
    swe = None

JST = ZoneInfo("Asia/Tokyo")
UTC = timezone.utc

STEMS = {
    "甲": ("木", "陽"), "乙": ("木", "陰"), "丙": ("火", "陽"), "丁": ("火", "陰"),
    "戊": ("土", "陽"), "己": ("土", "陰"), "庚": ("金", "陽"), "辛": ("金", "陰"),
    "壬": ("水", "陽"), "癸": ("水", "陰"),
}
BRANCHES = {
    "子": ("水", "陽"), "丑": ("土", "陰"), "寅": ("木", "陽"), "卯": ("木", "陰"),
    "辰": ("土", "陽"), "巳": ("火", "陰"), "午": ("火", "陽"), "未": ("土", "陰"),
    "申": ("金", "陽"), "酉": ("金", "陰"), "戌": ("土", "陽"), "亥": ("水", "陰"),
}
STEM_NAMES = tuple(STEMS)
BRANCH_NAMES = tuple(BRANCHES)
SEXAGENARY = tuple((STEM_NAMES[i % 10], BRANCH_NAMES[i % 12]) for i in range(60))

@dataclass(frozen=True)
class Character:
    id: str
    name: str
    element: str
    palette: str
    visual_signature: str
    keywords: tuple[str, ...]
    love_advice: str
    priority: int
    anchor_month_stem_element: str
    anchor_month_stem_polarity: str
    anchor_month_branch_element: str
    anchor_month_branch_polarity: str
    anchor_year_stem_element: str
    anchor_year_stem_polarity: str
    anchor_year_branch_element: str

CHARACTERS = (
    Character("moonlight_fox", "月灯りの白狐", "木", "ミント", "大きな耳・長い尾", ("知性", "直感", "柔軟性"), "駆け引きより素直な言葉を大切にする", 1, "木", "陽", "木", "陽", "水", "陰", "水"),
    Character("forest_fawn", "森隠れの子鹿", "木", "ミント", "枝角・花飾り", ("優しさ", "調和", "純粋さ"), "困ったことを早めに話す", 2, "木", "陰", "木", "陰", "土", "陰", "土"),
    Character("sunshine_lion", "陽だまりの獅子", "火", "ピーチ", "ふわふわのたてがみ", ("情熱", "行動力", "明るさ"), "相手のペースを尊重する", 1, "火", "陽", "火", "陽", "木", "陽", "火"),
    Character("sunrise_phoenix", "朝焼けの鳳凰", "火", "ピーチ", "大きな翼・炎の羽", ("希望", "社交性", "前向きさ"), "弱音も安心して共有する", 2, "火", "陰", "火", "陰", "火", "陰", "木"),
    Character("star_squirrel", "星の実りのリス", "火", "ピーチ", "大きなしっぽ・木の実", ("努力", "誠実", "成長"), "自分の疲れや希望も大切にする", 3, "土", "陽", "土", "陽", "土", "陽", "土"),
    Character("star_bear", "星読みの小熊", "土", "ミルクブラウン", "丸い耳・星のマント", ("安定", "誠実", "思いやり"), "小さな一歩から希望を伝える", 1, "土", "陽", "土", "陽", "土", "陽", "土"),
    Character("moonsea_otter", "月海のラッコ", "土", "ミルクブラウン", "貝殻・ふわふわのお腹", ("ぬくもり", "安心", "愛情"), "感謝を伝え、新しい体験も楽しむ", 2, "土", "陰", "土", "陰", "水", "陰", "水"),
    Character("stardew_rabbit", "星雫の月兎", "金", "ラベンダー", "垂れ耳・星の瞳・額の三日月", ("共感", "優しさ", "安心感"), "自分の気持ちも言葉にして伝える", 1, "金", "陽", "金", "陽", "金", "陽", "金"),
    Character("violet_cat", "紫宵の星猫", "金", "ラベンダー", "月模様・しなやかな尾", ("自由", "魅力", "独立心"), "大切に思う気持ちを言葉や行動で伝える", 2, "金", "陰", "金", "陰", "木", "陰", "木"),
    Character("moonowl", "月翔けのフクロウ", "金", "ラベンダー", "大きな羽・知的な目", ("洞察", "冷静", "知性"), "今の気持ちを少しずつ共有する", 3, "水", "陽", "水", "陽", "水", "陽", "水"),
    Character("seabreeze_dragon", "海風の星龍", "水", "水色", "小さな角・長いひげ・雲の尾", ("自由", "好奇心", "柔軟性"), "自分の時間と二人の時間を両立する", 1, "水", "陽", "水", "陽", "水", "陽", "水"),
    Character("watermirror_unicorn", "水鏡のユニコーン", "水", "水色", "星の角・流れるたてがみ", ("純粋", "理想", "ロマン"), "理想と同じくらい日常の幸せを見る", 2, "水", "陰", "水", "陰", "金", "陰", "金"),
)
BY_ELEMENT = {e: tuple(c for c in CHARACTERS if c.element == e) for e in ("木", "火", "土", "金", "水")}

@dataclass(frozen=True)
class Pillar:
    stem: str
    branch: str
    def __post_init__(self):
        if self.stem not in STEMS:
            raise ValueError(f"不正な天干: {self.stem}")
        if self.branch not in BRANCHES:
            raise ValueError(f"不正な地支: {self.branch}")

@dataclass(frozen=True)
class FourPillars:
    year: Pillar
    month: Pillar
    day: Pillar

@dataclass(frozen=True)
class Diagnosis:
    birth_datetime_jst: str
    year_pillar: str
    month_pillar: str
    day_pillar: str
    character_id: str
    character_name: str
    element: str
    palette: str
    keywords: tuple[str, ...]
    love_advice: str
    calendar_engine: str
    warnings: tuple[str, ...] = ()


def score_character(c: Character, p: FourPillars) -> tuple[int, int, int, int]:
    ms_e, ms_p = STEMS[p.month.stem]
    mb_e, mb_p = BRANCHES[p.month.branch]
    ys_e, ys_p = STEMS[p.year.stem]
    yb_e, _ = BRANCHES[p.year.branch]
    month_score = (4 * (ms_e == c.anchor_month_stem_element)
                   + 2 * (ms_p == c.anchor_month_stem_polarity)
                   + 3 * (mb_e == c.anchor_month_branch_element)
                   + 1 * (mb_p == c.anchor_month_branch_polarity))
    year_score = (2 * (ys_e == c.anchor_year_stem_element)
                  + 1 * (ys_p == c.anchor_year_stem_polarity)
                  + 1 * (yb_e == c.anchor_year_branch_element))
    return (month_score, year_score, -c.priority, 0)


def classify(pillars: FourPillars) -> Character:
    element = STEMS[pillars.day.stem][0]
    return max(BY_ELEMENT[element], key=lambda c: score_character(c, pillars))


def _julian_day(dt_utc: datetime) -> float:
    if swe is None:
        raise RuntimeError("暦計算には pyswisseph が必要です。pip install pyswisseph を実行してください。")
    dt_utc = dt_utc.astimezone(UTC)
    hour = dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600 + dt_utc.microsecond / 3_600_000_000
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour)


def solar_longitude(dt_jst: datetime) -> float:
    jd = _julian_day(dt_jst.astimezone(UTC))
    result, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
    return result[0] % 360


def _signed_angle_diff(a: float, b: float) -> float:
    return (a - b + 180) % 360 - 180


def _crosses_target(lon1: float, lon2: float, target: float) -> bool:
    # Over a short interval the Sun advances ~1 degree/day, so normalized
    # forward progress across the target is unambiguous.
    progress = (lon2 - lon1) % 360
    distance = (target - lon1) % 360
    return 0 < distance <= progress + 1e-9


def _find_term_near(start: datetime, target: float) -> datetime:
    """Find the solar-longitude crossing at target degrees after start."""
    lo = start
    lon_lo = solar_longitude(lo)
    hi = lo + timedelta(hours=6)
    # Search up to 40 days for a crossing.
    for _ in range(160):
        lon_hi = solar_longitude(hi)
        if _crosses_target(lon_lo, lon_hi, target):
            break
        lo, lon_lo = hi, lon_hi
        hi += timedelta(hours=6)
    else:
        raise RuntimeError(f"節気 {target}° を探索できませんでした")
    # Binary-search crossing instant.
    left, right = lo, hi
    for _ in range(42):
        mid = left + (right - left) / 2
        lon_mid = solar_longitude(mid)
        if _crosses_target(solar_longitude(left), lon_mid, target):
            right = mid
        else:
            left = mid
    return right


def _calculate_term_events(year: int) -> list[tuple[datetime, float]]:
    """All 24 solar terms for a Gregorian year, as JST instants."""
    start = datetime(year, 1, 1, tzinfo=JST)
    end = datetime(year + 1, 1, 1, tzinfo=JST)
    targets = tuple(float(x) for x in range(0, 360, 15))
    events = []
    left = start - timedelta(days=1)
    lon_left = solar_longitude(left)
    while left < end:
        right = min(left + timedelta(hours=6), end + timedelta(days=1))
        lon_right = solar_longitude(right)
        progress = (lon_right - lon_left) % 360
        for target in targets:
            distance = (target - lon_left) % 360
            if 1e-9 < distance <= progress + 1e-9:
                lo, hi = left, right
                for _ in range(42):
                    mid = lo + (hi - lo) / 2
                    lon_mid = solar_longitude(mid)
                    if _crosses_target(solar_longitude(lo), lon_mid, target):
                        hi = mid
                    else:
                        lo = mid
                event = hi
                if start <= event < end:
                    events.append((event, target))
        left, lon_left = right, lon_right
    events.sort()
    return events


@lru_cache(maxsize=1)
def _term_table():
    """Public astronomical data only: no user input or diagnosis is cached."""
    raw = json.loads(Path(__file__).with_name('solar_terms_jst.json').read_text())
    if raw.get('schema') != 1:
        raise RuntimeError('Unsupported solar term table schema')
    table = {}
    for year, rows in raw['years'].items():
        events = tuple((datetime.fromisoformat(dt).astimezone(JST), float(lon)) for dt, lon in rows)
        if len(events) != 24 or len({lon for _, lon in events}) != 24:
            raise RuntimeError('Invalid solar term table')
        if any(dt.year != int(year) or dt.utcoffset() not in (timedelta(hours=9), timedelta(hours=10)) for dt, _ in events):
            raise RuntimeError('Invalid solar term dates')
        if tuple(sorted(events)) != events:
            raise RuntimeError('Unsorted solar term table')
        table[int(year)] = events
    return table


@lru_cache(maxsize=32)
def _fallback_term_events(year):
    return tuple(_calculate_term_events(year))


def _term_events(year: int) -> list[tuple[datetime, float]]:
    # Return a fresh list, so callers cannot mutate the shared public table.
    table = _term_table()
    return list(table[year] if year in table else _fallback_term_events(year))


def _pillar_from_cycle(index: int) -> Pillar:
    stem, branch = SEXAGENARY[index % 60]
    return Pillar(stem, branch)


def calculate_four_pillars(birth_date: date | str, birth_time: time | str | None = None) -> tuple[FourPillars, datetime]:
    """Calculate year/month/day pillars. Input date/time is interpreted as JST.

    Month pillar switches at the 12 'jie' boundaries (315°, 345°, ..., 285°).
    Year pillar switches at 立春 (solar longitude 315°). Day pillar switches at
    00:00 JST. For date-only input, noon is used only to place the date relative
    to a solar-term boundary; day pillar still follows the entered date.
    """
    if swe is None:
        raise RuntimeError("この機能には pyswisseph が必要です。")
    if isinstance(birth_date, str):
        birth_date = date.fromisoformat(birth_date)
    if isinstance(birth_time, str):
        birth_time = time.fromisoformat(birth_time)
    if birth_time is None:
        birth_time = time(12, 0)
    dt = datetime.combine(birth_date, birth_time, tzinfo=JST)

    # Build events around the input year by finding the latest relevant solar terms.
    events = []
    for y in (birth_date.year - 1, birth_date.year, birth_date.year + 1):
        events.extend(_term_events(y))
    events.sort()
    lichun_events = [instant for instant, lon in events if lon == 315.0 and instant <= dt]
    if not lichun_events:
        raise RuntimeError("立春を特定できませんでした")
    lichun = lichun_events[-1]
    pillar_year = lichun.year
    year_cycle = (pillar_year - 1984) % 60
    year_pillar = _pillar_from_cycle(year_cycle)

    # Month branch: 寅 begins at 315°, then each 30° advances one branch.
    jie_targets = [315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285]
    month_events = [(instant, lon) for instant, lon in events if lon in jie_targets and instant <= dt]
    if not month_events:
        raise RuntimeError("月の節入りを特定できませんでした")
    month_start, month_lon = month_events[-1]
    month_index = jie_targets.index(int(month_lon))  # 0=寅, 1=卯, ... 11=丑
    year_stem_index = STEM_NAMES.index(year_pillar.stem)
    yin_stem_for_yin_month = ((year_stem_index % 5) * 2 + 2) % 10
    month_stem_index = (yin_stem_for_yin_month + month_index) % 10
    month_branch_index = (2 + month_index) % 12
    month_pillar = Pillar(STEM_NAMES[month_stem_index], BRANCH_NAMES[month_branch_index])

    # Day pillar: 2000-01-07 is used as 甲子 day-cycle anchor.
    # This anchor is a conventional arithmetic reference and should be validated
    # against the target calendar standard before production deployment.
    anchor = date(2000, 1, 7)
    day_cycle = (birth_date - anchor).days % 60
    day_pillar = _pillar_from_cycle(day_cycle)

    return FourPillars(year_pillar, month_pillar, day_pillar), dt


def diagnose(birth_date: date | str, birth_time: time | str | None = None) -> Diagnosis:
    pillars, dt = calculate_four_pillars(birth_date, birth_time)
    character = classify(pillars)
    def fmt(p: Pillar) -> str:
        return p.stem + p.branch
    warnings = []
    if birth_time is None:
        # A date-only entry cannot resolve whether birth was before/after a term
        # if the solar-term instant falls on that same local calendar date.
        for y in (dt.year - 1, dt.year, dt.year + 1):
            for instant, longitude in _term_events(y):
                if instant.date() == dt.date() and longitude in (315.0, 345.0, 15.0, 45.0, 75.0, 105.0, 135.0, 165.0, 195.0, 225.0, 255.0, 285.0):
                    warnings.append("出生時刻が未入力で、当日が節入り日に当たるため、年柱・月柱は仮に正午時点で判定しています。正確な判定には出生時刻を入力してください。")
                    break
            if warnings:
                break
    return Diagnosis(
        birth_datetime_jst=dt.isoformat(),
        year_pillar=fmt(pillars.year),
        month_pillar=fmt(pillars.month),
        day_pillar=fmt(pillars.day),
        character_id=character.id,
        character_name=character.name,
        element=character.element,
        palette=character.palette,
        keywords=character.keywords,
        love_advice=character.love_advice,
        calendar_engine="pyswisseph / solar-longitude search",
        warnings=tuple(warnings),
    )


def catalog_summary():
    return {"count": len(CHARACTERS), "distribution": {e: len(BY_ELEMENT[e]) for e in BY_ELEMENT},
            "characters": [asdict(c) for c in CHARACTERS]}


def self_test():
    assert len(CHARACTERS) == 12 and len({c.id for c in CHARACTERS}) == 12
    assert {e: len(BY_ELEMENT[e]) for e in BY_ELEMENT} == {"木": 2, "火": 3, "土": 2, "金": 3, "水": 2}
    # Verify cycle anchor and day-to-day progression.
    p0, _ = calculate_four_pillars("2000-01-07")
    p1, _ = calculate_four_pillars("2000-01-08")
    assert p0.day == Pillar("甲", "子"), f"anchor mismatch: {p0.day}"
    assert p1.day == Pillar("乙", "丑"), f"next-day mismatch: {p1.day}"
    known, _ = calculate_four_pillars("2000-01-07")
    assert known.year == Pillar("己", "卯"), f"year anchor mismatch: {known.year}"
    assert known.month == Pillar("丁", "丑"), f"month anchor mismatch: {known.month}"
    assert known.day == Pillar("甲", "子"), f"day anchor mismatch: {known.day}"
    # Boundary behavior around 立春, based on computed exact crossing.
    events = _term_events(2024)
    lichun = next(t for t, lon in events if lon == 315.0)
    before = lichun - timedelta(minutes=1)
    after = lichun + timedelta(minutes=1)
    bp, _ = calculate_four_pillars(before.date(), before.timetz().replace(tzinfo=None))
    ap, _ = calculate_four_pillars(after.date(), after.timetz().replace(tzinfo=None))
    assert bp.year != ap.year, (lichun, bp.year, ap.year)
    # Every sexagenary-cycle combination remains structurally valid.
    stems, branches = tuple(STEMS), tuple(BRANCHES)
    count = 0
    for ys, yb, ms, mb, ds, db in product(stems, branches, stems, branches, stems, branches):
        result = classify(FourPillars(Pillar(ys, yb), Pillar(ms, mb), Pillar(ds, db)))
        assert result.element == STEMS[ds][0]
        count += 1
    return f"OK: 12-character catalog; day anchor; 立春 boundary; {count:,} pillar combinations tested."


if __name__ == "__main__":
    print(self_test())
    print("2024-02-04 sample:", diagnose("2024-02-04"))
    print("Distribution:", catalog_summary()["distribution"])
