from io import BytesIO
from public_app import ProcessRateLimit
import public_app
clock = [0.0]
b = ProcessRateLimit(clock=lambda: clock[0])
assert all(b.allow() for _ in range(3))
assert not b.allow()
clock[0] = 4
assert b.allow() and not b.allow()
clock[0] = -10
assert not b.allow()
clock[0] = 8
assert b.allow()
# Each worker has independent capacity; never describe this as a shared/global limit.
assert ProcessRateLimit().allow()
public_app.DIAGNOSIS_LIMIT = ProcessRateLimit(rate=0, burst=0)
def call(path, method='GET'):
    out = {}
    def start(status, headers): out.update(status=status, headers=dict(headers))
    body=b''.join(public_app.application({'PATH_INFO':path,'REQUEST_METHOD':method,'CONTENT_LENGTH':'0','wsgi.input':BytesIO(b''),'HTTP_X_FORWARDED_FOR':'arbitrary'},start))
    return out, body
r,_=call('/diagnose','POST'); assert r['status'].startswith('429') and r['headers']['Retry-After']=='4'
for path in ['/', '/health','/source','/terms','/privacy','/commercial']:
    r,body=call(path); assert r['status']=='200 OK'
    assert '［'.encode() not in body and b'DRAFT' not in body
r,body=call('/privacy'); assert b'violed423@gmail.com' in body and b'Hobby' in body
assert not any(k in vars(public_app.DIAGNOSIS_LIMIT) for k in ['ip','answers','requests'])
print('OK: preview text, process-local rate control and health/source exemptions')
