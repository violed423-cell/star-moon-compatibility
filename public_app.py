"""Public-facing WSGI scaffold, standard-library HTTP handling, v1.7.
Run locally: python public_app.py
Deploy: gunicorn public_app:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30
No database, accounts, analytics, email, or payment processing is enabled.
"""
from datetime import date, datetime, timezone, timedelta
from html import escape
from io import BytesIO
import json
import os
import re
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from app_星月自動相性診断_v1_6 import page, form_html, get_answers, axis_html, ul, tags
from compatibility_v1_6 import make_profile, calculate_compatibility
from love_type_16_v1_4 import QUESTIONS, diagnose_answers

MAX_BODY = 64 * 1024

PREMIUM_BODY = '''<section class="hero"><h1>あの人との恋愛相性・関係性診断</h1><p>詳細レポートは準備中です。購入・決済はできません。</p></section><section class="panel"><h2>予定している内容</h2><p>8～12ページ程度で、2人の基本性格、恋愛傾向、相性の強み、すれ違いやすいポイント、関係を深めるヒントをお届けする予定です。</p><h2>価格案</h2><p>暫定 1,480円。販売開始前に内容・販売条件を確定します。</p><p class="warning">独自のエンターテインメント・自己理解用の参考情報であり、相手の気持ちや将来を断定するものではありません。</p><a href="/">無料診断に戻る</a></section>'''

TERMS_BODY = '''<section class="hero"><div class="eyebrow">DRAFT</div><h1>利用規約</h1><p>公開前に運営者情報・実際の提供内容に合わせて確認してください。</p></section><section class="panel"><h2>サービスの性質</h2><p>本サービスは独自ルールによるエンターテインメントおよび自己理解のための参考情報です。医療、心理診断、法律、金融その他の専門的助言ではなく、科学的に検証された予測でもありません。</p><h2>結果の利用</h2><p>診断結果は恋愛・交際・結婚の成否や将来を保証しません。結果だけで重要な決定を行わず、当事者同士の対話を大切にしてください。</p><h2>禁止事項</h2><p>法令違反、サービス運営の妨害、不正アクセス、他者の権利侵害、本人の同意を欠く個人情報の不適切な利用を禁止します。</p><h2>運営者・連絡先</h2><p>運営者：［正式な氏名または法人名］<br>連絡先：［問い合わせ先］<br>施行日：［公開日］</p></section>'''
PRIVACY_BODY = '''<section class="hero"><div class="eyebrow">DRAFT</div><h1>プライバシーポリシー</h1><p>実際のホスティング・アクセスログ・決済等の運用に合わせて公開前に更新してください。</p></section><section class="panel"><h2>取得情報・利用目的</h2><p>診断では生年月日、任意の出生時刻、恋愛スタイルの回答を受け取り、その場で結果を算出します。この試作品はアカウントや診断履歴を保存するデータベースを使用しません。</p><h2>サーバー・アクセスログ</h2><p>ホスティング事業者がIPアドレス、アクセス時刻、技術ログ等を取得する場合があります。公開前にログ仕様・保存期間を確認し、実態に合わせて修正してください。</p><h2>外部サービス</h2><p>現行版に分析タグ、広告タグ、決済連携は組み込んでいません。将来導入する場合は、送信情報・目的・提供事業者を確認して更新します。</p><h2>運営者・問い合わせ</h2><p>運営者：［正式な氏名または法人名］<br>連絡先：［問い合わせ先］<br>施行日：［公開日］</p></section>'''
COMMERCIAL_BODY = '''<section class="hero"><div class="eyebrow">DRAFT — PAID SALES NOT ENABLED</div><h1>特定商取引法に基づく表記</h1><p>現在は決済を受け付けていません。このページは記入用テンプレートです。空欄を残したまま有料販売を開始しないでください。</p></section><section class="panel"><p><b>販売事業者名：</b>［正式な氏名または法人名］</p><p><b>運営責任者：</b>［氏名］</p><p><b>所在地：</b>［必要な情報を記入］</p><p><b>電話番号：</b>［必要な情報を記入］</p><p><b>問い合わせ先：</b>［メールアドレス等］</p><p><b>販売価格：</b>［税込価格］</p><p><b>商品代金以外の必要料金：</b>［該当する場合］</p><p><b>支払方法・時期：</b>［決済手段・支払時期］</p><p><b>提供時期：</b>［購入後いつ提供するか］</p><p><b>キャンセル・返金条件：</b>［具体的な条件］</p><p><b>動作環境：</b>［対応端末・ブラウザ］</p><p class="warning">表示項目と例外の適用は、販売形態と現行法令を確認してください。</p></section>'''


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
    payload = page(body, title).replace(b'<head>', '<head><meta name="description" content="生年月日と恋愛スタイルから、ふたりの関係を見つめるヒントを届けます。">'.encode('utf-8'))
    nav = '<div style="margin-top:12px"><a href="/source">ソースコード（AGPL）</a> · <a href="/terms">利用規約（草案）</a> · <a href="/privacy">プライバシー（草案）</a> · <a href="/commercial">特商法表示テンプレート</a> · <a href="/premium">詳細レポート</a></div>'.encode('utf-8')
    payload = payload.replace(b'</div></main>', b'</div>' + nav + b'</main>')
    _headers(start_response, status)
    return [payload]


def _answers(form, key):
    return {q.id: form.get(f'{key}_{q.id}', [''])[0] for q in QUESTIONS}


def _result_body(da, db, a, b, love_a, love_b, r):
    warnings_html = ''.join(f'<p class="warning">{escape(profile.label)}：{escape(w)}</p>' for profile in (a, b) for w in profile.calendar_warnings)
    return f'''{warnings_html}<section class="hero"><div class="eyebrow">YOUR COMPATIBILITY</div><h1>ふたりの診断結果</h1><p>{escape(da)} × {escape(db)}</p></section><section class="result"><div class="eyebrow">REFERENCE SCORE</div><div class="score">{r.score}<small> / 100</small></div><div class="bar"><span style="width:{r.score}%"></span></div><h2>{escape(r.level)}</h2><p>{escape(r.explanation)}</p><div class="cols"><div class="box"><b>キャラクター相性（独自指標）</b><p>{r.character_score} / 100</p></div><div class="box"><b>恋愛スタイルの近さ</b><p>{r.love_type_score} / 100</p></div></div></section><section class="result"><h2>それぞれの診断結果</h2><div class="cols"><div class="box"><b>あなた</b><h3>{escape(a.character_name)}</h3><p>{escape(a.element)}・{escape(a.birth_date)}</p><h3>{escape(love_a.code)}｜{escape(love_a.name)}</h3><p>{escape(love_a.tagline)}</p><b>得意なこと</b><ul>{ul(love_a.strengths)}</ul><b>意識したいこと</b><ul>{ul(love_a.blind_spots)}</ul><p>{escape(love_a.advice)}</p><details><summary>4軸の回答結果</summary>{axis_html(love_a)}</details></div><div class="box"><b>お相手</b><h3>{escape(b.character_name)}</h3><p>{escape(b.element)}・{escape(b.birth_date)}</p><h3>{escape(love_b.code)}｜{escape(love_b.name)}</h3><p>{escape(love_b.tagline)}</p><b>得意なこと</b><ul>{ul(love_b.strengths)}</ul><b>意識したいこと</b><ul>{ul(love_b.blind_spots)}</ul><p>{escape(love_b.advice)}</p><details><summary>4軸の回答結果</summary>{axis_html(love_b)}</details></div></div></section><section class="result"><h2>共通しているところ</h2><p>{tags(r.shared_axes)}</p><ul>{ul(r.attraction_points)}</ul><h2>すり合わせのヒント</h2><p>{tags(r.different_axes)}</p><ul>{ul(r.friction_points)}</ul><h2>関係を育てるための提案</h2><ul>{ul(r.advice)}</ul></section><section class="panel"><h2>さらに詳しいレポート</h2><p>個別の読み解き、具体的な会話例、実践ワークシートなどを提供する構想です。現在は準備中で、決済はありません。</p><a class="button" href="/premium">詳細レポートの内容を見る</a><p><a class="back" href="/">← もう一度診断する</a></p></section>'''


def application(environ, start_response):
    method = environ.get('REQUEST_METHOD', 'GET').upper()
    path = environ.get('PATH_INFO', '/')
    if method == 'GET' and path == '/':
        body = form_html()
        # Add an explicit consent acknowledgement and honeypot field before the submit button.
        body = body.replace('<button type="submit">', '<label class="choice"><input type="checkbox" name="consent" value="yes" required><span>診断の注意事項とプライバシー説明を読み、入力することに同意します。</span></label><button type="submit">')
        body = body.replace('<form method="post">', '<form method="post" action="/diagnose"><div style="position:absolute;left:-10000px" aria-hidden="true"><label>入力しないでください<input name="website" tabindex="-1" autocomplete="off"></label></div>')
        body = body.replace('<button type="submit">', '<p class="warning">生年月日と回答は診断処理のためサーバーへ送信されます。この試作品は診断履歴をデータベースに保存しませんが、ホスティング事業者の技術ログは別途確認が必要です。相手の情報は本人の同意を得て入力してください。</p><button type="submit">')
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
        return _html(start_response, PREMIUM_BODY, '詳細レポート | 星と月')
    if method == 'GET' and path == '/terms':
        return _html(start_response, TERMS_BODY, '利用規約（草案） | 星と月')
    if method == 'GET' and path == '/privacy':
        return _html(start_response, PRIVACY_BODY, 'プライバシーポリシー（草案） | 星と月')
    if method == 'GET' and path == '/commercial':
        return _html(start_response, COMMERCIAL_BODY, '特定商取引法に基づく表記（テンプレート） | 星と月')
    if method == 'POST' and path == '/diagnose':
        try:
            raw_len = int(environ.get('CONTENT_LENGTH') or '0')
            if raw_len < 0 or raw_len > MAX_BODY:
                raise ValueError('入力サイズが大きすぎます。')
            raw = environ['wsgi.input'].read(raw_len).decode('utf-8', 'strict')
            f = parse_qs(raw, keep_blank_values=True, max_num_fields=100)
            if f.get('website', [''])[0].strip():
                raise ValueError('フォームを再読み込みしてお試しください。')
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
            birth_a, birth_b = date.fromisoformat(da), date.fromisoformat(db)
            today = datetime.now(timezone(timedelta(hours=9))).date()
            if birth_a > today or birth_b > today:
                raise ValueError('生年月日は今日以前の日付を入力してください。')
            if birth_a.year < 1900 or birth_b.year < 1900:
                raise ValueError('生年月日は1900年以降を入力してください。')
            love_a = diagnose_answers(_answers(f, 'a')); love_b = diagnose_answers(_answers(f, 'b'))
            a = make_profile('あなた', da, love_a.code, birth_time=ta)
            b = make_profile('お相手', db, love_b.code, birth_time=tb)
            r = calculate_compatibility(a, b)
            return _html(start_response, _result_body(da, db, a, b, love_a, love_b, r), '相性診断結果 | 星と月')
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
