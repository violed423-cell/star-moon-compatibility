from unittest.mock import patch
from test_public_app import call

def main():
    r,b=call('/')
    assert b'/source' in b
    sha='a'*40
    with patch.dict('os.environ', {'RENDER_GIT_COMMIT':sha}):
        r,b=call('/source')
    assert r['status']=='200 OK'
    assert ('/tree/'+sha).encode() in b and ('/archive/'+sha+'.zip').encode() in b
    with patch.dict('os.environ', {'RENDER_GIT_COMMIT':'<invalid>'}):
        r,b=call('/source')
    assert b'/tree/main' in b and b'<invalid>' not in b
    print('OK: network source offer and deployed revision link')
if __name__=='__main__':main()
