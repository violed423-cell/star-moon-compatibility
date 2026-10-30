"""Regression tests for verified handoff corrections, using synthetic inputs only."""
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
import independent_12_animal_diagnosis_v1_3 as cal
from test_public_app import call

def main():
    assert {e:len(v) for e,v in cal.BY_ELEMENT.items()} == {'木':2,'火':3,'土':2,'金':3,'水':2}
    p = cal.FourPillars(cal.Pillar('丙','寅'),cal.Pillar('甲','卯'),cal.Pillar('丙','子'))
    assert cal.classify(p).id == 'sunshine_lion', 'Monthly score must precede yearly score'
    f = {'date_a':'2024-02-04','date_b':'2000-01-07','consent':'yes'}
    for person in ('a','b'):
        for i in range(1,13): f[f'{person}_q{i}']='A'
    r,b=call('/diagnose','POST',f)
    assert r['status']=='200 OK'
    assert '正午時点'.encode() in b, 'Unknown birth time boundary warning must reach user'
    r,b=call('/premium')
    assert '1,480円'.encode() in b and '8～12ページ'.encode() in b
    class JSTClock(datetime):
        @classmethod
        def now(cls,tz=None):
            assert tz.utcoffset(None)==timedelta(hours=9)
            return cls(2026,10,30,0,30,tzinfo=tz)
    f['date_a']='2026-10-30'
    with patch('public_app.datetime',JSTClock):
        r,b=call('/diagnose','POST',f)
    assert r['status']=='200 OK', 'Today must be based on JST, not server UTC'
    print('OK: latest distribution, monthly priority, calendar warning, price, JST date boundary')

if __name__=='__main__': main()
