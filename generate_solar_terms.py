"""Offline reproducible public ephemeris table; run explicitly, never per request.
Default coverage 1899..2027 supports all web birth dates 1900..2026.
Regenerate and test annually before expanding the supported current year.
"""
import json
from pathlib import Path
import independent_12_animal_diagnosis_v1_3 as cal

def generate(start=1899, end=2027):
    data={str(y):[[dt.isoformat(),lon] for dt,lon in cal._calculate_term_events(y)] for y in range(start,end+1)}
    return {'schema':1,'generator':'pyswisseph 2.10.3.2; original v1.9 six-hour scan and 42 bisections; JST','years':data}
if __name__=='__main__':
    Path(__file__).with_name('solar_terms_jst.json').write_text(json.dumps(generate(),ensure_ascii=False,separators=(',',':'))+'\n')
