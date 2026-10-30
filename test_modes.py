from test_public_app import call
from compatibility_v1_6 import make_profile, calculate_compatibility
from love_type_16_v1_4 import diagnose_answers
form={'date_a':'2000-01-07','date_b':'2001-03-21','consent':'yes'}
def answers(key): return {f'{key}_q{i}':'A' for i in range(1,13)}
r,b=call('/'); assert r['status']=='200 OK'
for mode in ('birth','self','both'):
    assert f'href="/{mode}"'.encode() in b
    r,h=call('/'+mode); assert r['status']=='200 OK'
    assert f'name="mode" value="{mode}"'.encode() in h
    assert (b'name="a_q1"' in h)==(mode!='birth')
    assert (b'name="b_q1"' in h)==(mode=='both')
    assert b'action="/diagnose"' in h and b'name="consent"' in h
    f=dict(form,mode=mode)
    if mode!='birth': f.update(answers('a'))
    if mode=='both': f.update(answers('b'))
    r,result=call('/diagnose','POST',f); assert r['status']=='200 OK', (mode,result[-200:])
    assert b' / 100' in result and b'/source' in result
    if mode!='both': assert '総合点は未算出'.encode() in result
    if mode=='self': assert 'お相手の恋愛タイプは未診断'.encode() in result
    r,_=call('/diagnose','POST',{k:v for k,v in f.items() if k!='consent'}); assert r['status'].startswith('400')
    r,_=call('/diagnose','POST',dict(f,date_a='1899-01-01')); assert r['status'].startswith('400')
    if mode!='birth':
        r,_=call('/diagnose','POST',{k:v for k,v in f.items() if k!='a_q1'}); assert r['status'].startswith('400')
    if mode=='both':
        r,_=call('/diagnose','POST',{k:v for k,v in f.items() if k!='b_q1'}); assert r['status'].startswith('400')
# Unused partner answers cannot influence the self-only result.
f=dict(form,mode='self',**answers('a'))
assert call('/diagnose','POST',f)[1]==call('/diagnose','POST',dict(f,b_q1='INVALID'))[1]
r,_=call('/diagnose','POST',dict(form,mode='unknown')); assert r['status'].startswith('400')
# Existing full score remains unchanged.
love=diagnose_answers({f'q{i}':'A' for i in range(1,13)})
expected=calculate_compatibility(make_profile('a',form['date_a'],love.code),make_profile('b',form['date_b'],love.code)).score
r,b=call('/diagnose','POST',dict(form,mode='both',**answers('a'),**answers('b')))
assert f'>{expected}<small>'.encode() in b
print('OK: three modes, strict required fields, unknown partner not inferred, existing full score preserved')
