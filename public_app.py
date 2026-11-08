"""Public-facing WSGI scaffold, standard-library HTTP handling, v1.7.
Run locally: python public_app.py
Deploy: gunicorn public_app:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30
No database, accounts, analytics, email, or payment processing is enabled.
"""
from datetime import date, datetime, timezone, timedelta
from html import escape
import json
import os
import re
import threading
import time
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from app_星月自動相性診断_v1_6 import page
from love_type_16_v1_4 import QUESTIONS

import fortune_ui
import fortune_content

MAX_BODY = 64 * 1024



TERMS_BODY = '''<section class="hero"><h1>利用規約</h1><p>星と月は無料の試験公開サービスです。</p></section><section class="panel"><h2>診断について</h2><p>独自の分類によるエンターテインメント・自己理解用の参考情報です。科学的な心理検査や、相手の気持ち・未来の予測ではありません。結果だけで重要な判断をせず、当事者同士の対話を大切にしてください。</p><h2>利用上のお願い</h2><p>相手の生年月日等は本人の同意を得て入力してください。不正アクセス、過剰な連続送信、サービス妨害、第三者の権利を侵害する利用は禁止します。試験公開中は機能の変更・停止や接続の遅延があり得ます。このサイト上で料金の請求や有料商品の購入受付は行いません。鑑定書は準備中で、販売先へのリンクは掲載していません。</p><h2>運営・問い合わせ</h2><p>星と月 運営<br><a href="mailto:violed423@gmail.com">violed423@gmail.com</a></p></section>'''
PRIVACY_BODY = '''<section class="hero"><h1>プライバシーポリシー</h1></section><section class="panel"><h2>入力情報の利用</h2><p>生年月日、任意の出生時刻、恋愛スタイルの回答をサーバーへ送信し、その場で診断結果を計算します。処理中はメモリを使用しますが、アプリは入力内容・結果をデータベースやファイルに保存せず、診断履歴を作りません。入力本文や結果をアプリのログへ出力しません。</p><h2>外部サービス・ログ</h2><p>ホスティングには Render を利用します。接続やサービス運用に必要な技術情報は同社の処理対象となります。現在の Hobby ワークスペースのダッシュボードログ保持期間は7日です。これは Render が扱うすべてのデータの削除期限を保証するものではありません。アプリ独自の入力本文・診断結果ログは出力しませんが、ホストやWebサーバーの技術・アクセスログは別途生成される場合があります。分析タグ、広告タグ、決済、会員登録、メール自動送信は組み込んでいません。</p><h2>送信回数の制御</h2><p>過負荷防止のため各処理プロセスで送信回数を一時的に数えます。IPアドレスや回答をこの制御のために記録しません。他の利用者の送信により一時的に利用できない場合は、時間をおいてお試しください。</p><h2>問い合わせ</h2><p>星と月 運営<br><a href="mailto:violed423@gmail.com">violed423@gmail.com</a></p></section>'''

class ProcessRateLimit:
    """Process-local aggregate token bucket, not per-user or distributed protection."""
    def __init__(self, rate=15 / 60, burst=3, clock=time.monotonic):
        self.rate, self.burst, self.clock = rate, burst, clock
        self.tokens, self.updated = float(burst), clock()
        self.lock = threading.Lock()

    def allow(self):
        with self.lock:
            now = self.clock()
            elapsed = max(0.0, now - self.updated)
            self.updated = max(now, self.updated)
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            if self.tokens < 1:
                return False
            self.tokens -= 1
            return True

DIAGNOSIS_LIMIT = ProcessRateLimit()


def _headers(start_response, status='200 OK', content_type='text/html; charset=utf-8'):
    headers = [
        ('Content-Type', content_type),
        ('Cache-Control', 'no-store'),
        ('X-Content-Type-Options', 'nosniff'),
        ('X-Frame-Options', 'DENY'),
        ('Referrer-Policy', 'strict-origin-when-cross-origin'),
        ('Permissions-Policy', 'camera=(), microphone=(), geolocation=()'),
        ('Cross-Origin-Opener-Policy', 'same-origin'),
        ('Content-Security-Policy', "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; form-action 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'"),
    ]
    start_response(status, headers)


def _html(start_response, body, title='星と月｜ふたりの相性診断', status='200 OK'):
    body = fortune_ui.ornaments.decorate_body(body)
    payload = page(body, title).replace(b'</style>', (fortune_ui.STYLE + '</style>').encode()).replace(b'<head>', '<head><meta name="description" content="生年月日と恋愛スタイルから、ふたりの関係を見つめるヒントを届けます。">'.encode('utf-8'))
    nav = '<div class="footer-nav"><a href="/source">ソースコード（AGPL）</a> · <a href="/terms">利用規約</a> · <a href="/privacy">プライバシー</a> · <a href="/premium">鑑定書</a></div>'.encode('utf-8')
    payload = payload.replace(b'</div></main>', b'</div>' + nav + b'</main>')
    _headers(start_response, status)
    return [payload]


def _answers(form, key):
    return {q.id: form.get(f'{key}_{q.id}', [''])[0] for q in QUESTIONS}




def application(environ, start_response):
    method = environ.get('REQUEST_METHOD', 'GET').upper()
    path = environ.get('PATH_INFO', '/')
    if method == 'GET' and path == fortune_content.ARTWORK_URL:
        data = fortune_content.artwork_bytes()
        if data is None:
            _headers(start_response, '404 Not Found', 'text/plain; charset=utf-8')
            return ['画像は準備中です。'.encode('utf-8')]
        _headers(start_response, content_type='image/jpeg')
        return [data]
    if path == '/both':
        return _html(start_response, fortune_ui.premium_page(), '有料診断は準備中 | 星と月', '403 Forbidden')
    if method == 'GET' and path in ('/', '/free', '/birth', '/self'):
        body = fortune_ui.free_form()
        # Add an explicit consent acknowledgement and honeypot field before the submit button.
        body = body.replace('<button type="submit">', '<label class="choice"><input type="checkbox" name="consent" value="yes" required><span>診断の注意事項とプライバシー説明を読み、入力することに同意します。</span></label><button type="submit">')
        body = body.replace('<form method="post">', '<form method="post" action="/diagnose"><div style="position:absolute;left:-10000px" aria-hidden="true"><label>入力しないでください<input name="website" tabindex="-1" autocomplete="off"></label></div>')
        body = body.replace('<button type="submit">', '<p class="warning">生年月日と回答は診断処理のためサーバーへ送信されます。この試作品は診断履歴をデータベースに保存しませんが、ホスティング事業者は運用上の技術情報を処理します。詳細はプライバシーポリシーをご確認ください。相手の情報は本人の同意を得て入力してください。</p><button type="submit">')
        return _html(start_response, body)
    if method == 'GET' and path == '/source':
        revision = os.environ.get('RENDER_GIT_COMMIT', '')
        ref = revision if re.fullmatch(r'[0-9a-fA-F]{40}', revision) else 'main'
        source_url = 'https://github.com/violed423-cell/star-moon-compatibility/tree/' + ref
        archive_url = 'https://github.com/violed423-cell/star-moon-compatibility/archive/' + ref + '.zip'
        return _html(start_response, f'<section class="panel"><h1>ソースコード</h1><p>このサービスは GNU AGPL v3 の条件で提供されています。</p><p><a href="{source_url}">ソースコード・構築手順・ライセンス</a></p><p><a href="{archive_url}">対応ソース ZIP をダウンロード</a></p><p>配布内容には保証はありません。依存ライブラリの条件もリポジトリ内に記載しています。</p></section>', 'ソースコード | 星と月')
    if method == 'GET' and path == '/health':
        payload = json.dumps({'status':'ok','version':'1.9-release-candidate'}).encode()
        _headers(start_response, content_type='application/json; charset=utf-8')
        return [payload]
    if method == 'GET' and path == '/premium':
        return _html(start_response, fortune_ui.premium_page(), '鑑定書 | 星と月')
    if method == 'GET' and path == '/terms':
        return _html(start_response, TERMS_BODY, '利用規約 | 星と月')
    if method == 'GET' and path == '/privacy':
        return _html(start_response, PRIVACY_BODY, 'プライバシーポリシー | 星と月')
    if method == 'GET' and path == '/commercial':
        return _html(start_response, '<section class="hero"><h1>販売について</h1></section>' + fortune_ui.premium_page(), '販売について | 星と月')
    if method == 'POST' and path == '/diagnose':
        if not DIAGNOSIS_LIMIT.allow():
            def limited_response(status, headers):
                return start_response(status, headers + [('Retry-After', '4')])
            return _html(limited_response, '<section class="panel"><h1>少し時間をおいてください</h1><p>送信が集中しています。しばらく待ってから再度お試しください。</p></section>', status='429 Too Many Requests')
        try:
            raw_len = int(environ.get('CONTENT_LENGTH') or '0')
            if raw_len < 0 or raw_len > MAX_BODY:
                raise ValueError('入力サイズが大きすぎます。')
            raw = environ['wsgi.input'].read(raw_len).decode('utf-8', 'strict')
            f = parse_qs(raw, keep_blank_values=True, max_num_fields=100)
            scalar_fields = {'date_a', 'date_b', 'time_a', 'time_b', 'consent', 'website'} | {f'a_{q.id}' for q in QUESTIONS}
            if any(len(f[key]) != 1 for key in scalar_fields if key in f):
                raise ValueError('入力が重複しています。フォームからやり直してください。')
            if f.get('website', [''])[0].strip():
                raise ValueError('フォームを再読み込みしてお試しください。')
            mode_values = f.get('mode', ['free'])
            if mode_values == ['both']:
                return _html(start_response, fortune_ui.premium_page(), '有料診断は準備中 | 星と月', '403 Forbidden')
            if mode_values != ['free']:
                raise ValueError('無料診断のページからやり直してください。')
            opt_in = f.get('include_self', [])
            if opt_in not in ([], ['yes']):
                raise ValueError('12問に回答するか選び直してください。')
            mode = 'self' if opt_in == ['yes'] else 'birth'
            da = f.get('date_a', [''])[0]; db = f.get('date_b', [''])[0]
            ta = f.get('time_a', [''])[0] or None; tb = f.get('time_b', [''])[0] or None
            if f.get('consent', [''])[0] != 'yes':
                raise ValueError('診断の注意事項とプライバシー説明への同意が必要です。')
            if not da or not db:
                raise ValueError('2人分の生年月日を入力してください。')
            for label, value in (('あなた', ta), ('お相手', tb)):
                if value is not None:
                    if not re.fullmatch(r'\d{2}:\d{2}', value):
                        raise ValueError(f'{label}の出生時刻は時:分の形式で入力してください。')
                    try:
                        datetime.strptime(value, '%H:%M')
                    except ValueError:
                        raise ValueError(f'{label}の出生時刻が正しくありません。')
            try:
                if not all(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) for value in (da, db)):
                    raise ValueError
                birth_a, birth_b = date.fromisoformat(da), date.fromisoformat(db)
            except ValueError:
                raise ValueError('生年月日を正しい日付で入力してください。')
            today = datetime.now(timezone(timedelta(hours=9))).date()
            if birth_a > today or birth_b > today:
                raise ValueError('生年月日は今日以前の日付を入力してください。')
            if birth_a.year < 1900 or birth_b.year < 1900:
                raise ValueError('生年月日は1900年以降を入力してください。')
            love = fortune_content.read_self_answers(_answers(f, 'a')) if mode == 'self' else None
            return _html(start_response, fortune_ui.partial_result(mode, da, db, ta, tb, love), '星と月の診断結果')
        except (ValueError, UnicodeDecodeError) as exc:
            return _html(start_response, f'<section class="panel"><h1>入力を確認してください</h1><p>{escape(str(exc))}</p><a class="back" href="/">戻る</a></section>', '入力エラー | 星と月', '400 Bad Request')
        except Exception:
            # Do not expose internal exception details to visitors.
            return _html(start_response, '<section class="panel"><h1>一時的なエラーが発生しました</h1><p>入力内容を確認して、時間をおいてもう一度お試しください。</p><a class="back" href="/">トップへ戻る</a></section>', 'サーバーエラー | 星と月', '500 Internal Server Error')
    if method not in ('GET', 'POST'):
        _headers(start_response, '405 Method Not Allowed', 'text/plain; charset=utf-8')
        return ['Method Not Allowed'.encode('utf-8')]
    return _html(start_response, '<section class="panel"><h1>ページが見つかりません</h1><a class="back" href="/">トップへ戻る</a></section>', 'Not Found | 星と月', '404 Not Found')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8003'))
    print(f'星と月 公開候補版 v1.9: http://127.0.0.1:{port}')
    with make_server('127.0.0.1', port, application) as server:
        server.serve_forever()
