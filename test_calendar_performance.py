"""Equivalence is against original algorithm, not independent calendar certification."""
from datetime import datetime, timedelta
from unittest.mock import patch
from time import perf_counter
import independent_12_animal_diagnosis_v1_3 as cal
from test_public_app import call

for y in (1899,1900,1950,2000,2024,2026,2027):
    saved, computed = cal._term_events(y), cal._calculate_term_events(y)
    assert len(saved) == len(computed) == 24
    differences = [abs((a[0]-b[0]).total_seconds()) for a,b in zip(saved,computed)]
    print('ephemeris platform difference', y, max(differences), 'seconds')
    assert all(a[1] == b[1] for a,b in zip(saved,computed))
    assert max(differences) <= 0.001, (y, max(differences), saved[0], computed[0])
# Mutation cannot corrupt shared ephemeris data.
a=cal._term_events(2024); a.clear(); assert len(cal._term_events(2024))==24
form={'date_a':'1900-01-01','date_b':datetime.now(cal.JST).date().isoformat(),'consent':'yes'}
for person in ('a','b'):
    for n in range(1,13): form[f'{person}_q{n}']='A'
cal._term_table.cache_clear()
t=perf_counter()
# Proves a cold normal request performs zero expensive ephemeris calculations.
with patch.object(cal,'solar_longitude',side_effect=AssertionError('unexpected runtime ephemeris')):
    response, body=call('/diagnose','POST',form)
    assert response['status']=='200 OK'
    for dt,lon in cal._term_events(2024):
        if lon==315:
            before,_=cal.calculate_four_pillars(dt.date(),(dt-timedelta(seconds=1)).time())
            after,_=cal.calculate_four_pillars(dt.date(),(dt+timedelta(seconds=1)).time())
            assert before.year!=after.year and before.month!=after.month
elapsed=perf_counter()-t
assert elapsed < 2, elapsed
print(f'OK: original event equivalence within 1 ms across builds; cold two-person POST {elapsed:.4f}s; zero runtime ephemeris calls')
