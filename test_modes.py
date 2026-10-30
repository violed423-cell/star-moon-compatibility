from test_public_app import call
from unittest.mock import patch
form={'date_a':'2000-01-07','date_b':'2001-03-21','consent':'yes','mode':'free'}
answers={f'a_q{i}':'A' for i in range(1,13)}
for path in ('/','/free','/birth','/self'):
    r,h=call(path); assert r['status']=='200 OK'
    assert b'name="include_self" value="yes"' in h
    assert b'name="include_self" value="yes" checked' not in h
    assert b'name="b_q1"' not in h
    assert b'name="a_q1" value="A" required' not in h
    assert b'name="mode" value="free"' in h
# Off never calls questionnaire classifier, even with stale/invalid answers.
with patch('public_app.diagnose_answers',side_effect=AssertionError('must not classify when opt-out')):
    r,base=call('/diagnose','POST',form); assert r['status']=='200 OK'
    assert base==call('/diagnose','POST',dict(form,a_q1='INVALID'))[1]
    assert 'あなたの恋愛スタイル'.encode() not in base
r,result=call('/diagnose','POST',dict(form,include_self='yes',**answers))
assert r['status']=='200 OK' and 'あなたの恋愛スタイル'.encode() in result
assert 'お相手の恋愛タイプは未診断'.encode() in result
for f in [dict(form,include_self='yes'),dict(form,include_self='no'),dict(form,include_self=['yes','yes']),dict(form,mode='self'),dict(form,mode=['free','both'])]:
    r,_=call('/diagnose','POST',f); assert r['status'].startswith('400'),f
for f in [dict(form,mode='both',**answers),dict(form,mode='both',paid='true',entitled='yes')]:
    r,h=call('/diagnose','POST',f); assert r['status'].startswith('403') and '準備中'.encode() in h
for method in ('GET','POST'):
    r,h=call('/both',method,dict(form,**answers)); assert r['status'].startswith('403')
# Both birth dates and consent remain mandatory regardless of opt-in.
for missing in ('date_a','date_b','consent'):
    r,_=call('/diagnose','POST',{k:v for k,v in form.items() if k!=missing}); assert r['status'].startswith('400')
r,h=call('/premium'); assert r['status']=='200 OK' and '現在は利用・購入・決済できません'.encode() in h
print('OK: unified free form; explicit optional self answers; no premium URL/POST bypass; no fake payment')
