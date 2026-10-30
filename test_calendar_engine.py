"""Calendar regression checks for the Four Pillars prototype.
Run: python test_calendar_engine.py
These checks are sanity/regression tests, not a substitute for expert calendar validation.
"""
from datetime import datetime, timedelta
import independent_12_animal_diagnosis_v1_3 as cal


def main():
    # Conventional day-cycle anchor and midnight-based day progression.
    p0, _ = cal.calculate_four_pillars('2000-01-07', '23:59')
    p1, _ = cal.calculate_four_pillars('2000-01-08', '00:00')
    assert (p0.day.stem, p0.day.branch) == ('甲', '子')
    assert (p1.day.stem, p1.day.branch) == ('乙', '丑')

    # Published Japanese calendar references: 2024 Lichun is around 17:27 JST;
    # test a margin on either side rather than pretending minute-level precision
    # is the same thing as full authoritative-calendar validation.
    events_2024 = cal._term_events(2024)
    assert len(events_2024) == 24
    lichun_2024 = next(dt for dt, longitude in events_2024 if longitude == 315.0)
    reference = datetime(2024, 2, 4, 17, 27, tzinfo=cal.JST)
    assert abs((lichun_2024 - reference).total_seconds()) < 180, lichun_2024

    before, _ = cal.calculate_four_pillars('2024-02-04', '17:26')
    after, _ = cal.calculate_four_pillars('2024-02-04', '17:28')
    assert before.year != after.year
    assert before.month != after.month
    assert (before.year.stem, before.year.branch) == ('癸', '卯')
    assert (after.year.stem, after.year.branch) == ('甲', '辰')
    assert (after.month.stem, after.month.branch) == ('丙', '寅')

    # Sample historical, present, and future years to keep CI runtime reasonable.
    # Full 1900-2100 validation is intentionally a separate offline task.
    years = [1900, 1950, 2000, *range(2020, 2031), 2050, 2100]
    for year in years:
        events = cal._term_events(year)
        assert len(events) == 24, (year, len(events))
        assert all(events[i][0] < events[i + 1][0] for i in range(23)), year

    # Every representative date should produce a character from the day-stem element group.
    for d in ('1900-01-01', '1945-08-15', '1989-01-08', '2000-01-07', '2024-02-04', '2026-10-18', '2100-12-31'):
        result = cal.diagnose(d)
        assert result.character_id and result.character_name
        assert result.year_pillar and result.month_pillar and result.day_pillar

    print(f'OK: day-cycle anchor, Lichun boundary, {len(years)} sampled years × 24 solar terms, sample diagnosis dates')

if __name__ == '__main__':
    main()
