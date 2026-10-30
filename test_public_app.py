"""Smoke tests for the public WSGI scaffold; run: python test_public_app.py"""
from io import BytesIO
from urllib.parse import urlencode
from public_app import application


def call(path='/', method='GET', form=None):
    import public_app
    public_app.DIAGNOSIS_LIMIT = public_app.ProcessRateLimit()
    data = urlencode(form or {}).encode('utf-8')
    environ = {
        'REQUEST_METHOD': method, 'PATH_INFO': path,
        'CONTENT_LENGTH': str(len(data)), 'wsgi.input': BytesIO(data),
        'SERVER_NAME': 'localhost', 'SERVER_PORT': '8003', 'wsgi.url_scheme': 'http',
    }
    result = {}
    def start_response(status, headers):
        result['status'] = status
        result['headers'] = dict(headers)
    body = b''.join(application(environ, start_response))
    return result, body


def main():
    response, body = call('/both')
    assert response['status'] == '200 OK' and 'ふたりの生年月日'.encode() in body
    assert 'サーバーへ送信'.encode() in body and 'consent'.encode() in body
    assert response['headers']['Cache-Control'] == 'no-store'
    response, body = call('/health')
    assert response['status'] == '200 OK' and b'"status": "ok"' in body and b'1.9-release-candidate' in body
    response, body = call('/premium')
    assert response['status'] == '200 OK' and '価格案'.encode() in body and '決済'.encode() in body and '1,480円'.encode() in body and '500〜980円'.encode() not in body
    response, body = call('/terms')
    assert response['status'] == '200 OK' and '利用規約'.encode() in body
    response, body = call('/privacy')
    assert response['status'] == '200 OK' and 'プライバシーポリシー'.encode() in body
    response, body = call('/commercial')
    assert response['status'] == '200 OK' and '販売について'.encode() in body
    form = {'date_a': '2000-01-07', 'date_b': '2001-03-21', 'consent': 'yes'}
    for person in ('a', 'b'):
        for i in range(1, 13):
            form[f'{person}_q{i}'] = 'A' if i % 2 else 'B'
    response, body = call('/diagnose', 'POST', form)
    assert response['status'] == '200 OK', body[:500]
    assert 'ふたりの診断結果'.encode() in body and b'/ 100' in body
    response, body = call('/diagnose', 'POST', {'date_a': '2000-01-01', 'date_b': '2001-01-01', 'consent': 'yes'})
    assert response['status'] == '400 Bad Request'
    response, body = call('/diagnose', 'POST', {'date_a': '2000-01-01', 'date_b': '2001-01-01'})
    assert response['status'] == '400 Bad Request' and '同意'.encode() in body
    response, body = call('/diagnose', 'POST', {'date_a': '1899-12-31', 'date_b': '2001-01-01', 'consent': 'yes'})
    assert response['status'] == '400 Bad Request' and '1900年以降'.encode() in body
    response, body = call('/diagnose', 'POST', {'date_a': '2000-01-01', 'date_b': '2001-01-01', 'time_a': '25:99', 'consent': 'yes'})
    assert response['status'] == '400 Bad Request' and '出生時刻'.encode() in body
    response, body = call('/diagnose', 'POST', {'date_a': '2030-01-01', 'date_b': '2001-01-01', 'consent': 'yes'})
    assert response['status'] == '400 Bad Request' and '今日以前'.encode() in body
    response, body = call('/diagnose', 'POST', {'date_a': '2000-01-01', 'date_b': '2001-01-01', 'consent': 'yes', 'a_q1': 'X'})
    assert response['status'] == '400 Bad Request' and '回答が不足'.encode() in body
    assert response['headers']['X-Frame-Options'] == 'DENY'
    assert "object-src 'none'" in response['headers']['Content-Security-Policy']
    response, body = call('/unknown')
    assert response['status'] == '404 Not Found'
    response, body = call('/diagnose', 'PUT', {})
    assert response['status'] == '405 Method Not Allowed' and response['headers']['X-Content-Type-Options'] == 'nosniff'
    print('OK: WSGI routes, consent, date/time/answer validation, method handling, and security headers passed')

if __name__ == '__main__':
    main()
