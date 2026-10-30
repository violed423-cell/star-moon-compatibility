import sys
sys.path.insert(0, '/mnt/data')
from love_type_16_v1_4 import QUESTIONS, diagnose_answers, TYPES
from compatibility_v1_6 import make_profile, calculate_compatibility

# All 16 codes are reachable through the 12-question answer flow.
for code in TYPES:
    answers={q.id: ('A' if code[q.axis]=='0' else 'B') for q in QUESTIONS}
    assert diagnose_answers(answers).code == code
# Profile generation from birth date and automatically detected love type.
a=make_profile('A','1990-06-15', '0000')
b=make_profile('B','1992-11-03', '1111')
r=calculate_compatibility(a,b)
assert a.character_id and b.character_id and 0 <= r.score <= 100
assert len(r.shared_axes)+len(r.different_axes)==4
# Missing answers should be rejected.
try: diagnose_answers({})
except ValueError: pass
else: raise AssertionError('missing answers accepted')
print('OK: 16 love types reachable; automatic profiles; compatibility result; missing-answer validation.')
