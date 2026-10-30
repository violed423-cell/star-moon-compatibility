"""星と月 自動相性診断 v1.6
Run: python app_星月自動相性診断_v1_6.py
Open: http://127.0.0.1:8002
Local demo only; no account, database, or public hosting.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from html import escape
from datetime import date
from compatibility_v1_6 import make_profile, calculate_compatibility
from love_type_16_v1_4 import QUESTIONS, AXES, diagnose_answers

HOST, PORT = "127.0.0.1", 8002
STYLE = r"""
*{box-sizing:border-box}body{margin:0;background:linear-gradient(135deg,#fbf9ff,#eef6ff);font-family:system-ui,-apple-system,sans-serif;color:#29263a}main{max-width:900px;margin:0 auto;padding:24px 16px 56px}.hero{padding:20px 4px}.eyebrow{color:#7664a8;font-size:12px;letter-spacing:.12em;font-weight:800}.hero h1{font-size:clamp(28px,6vw,40px);line-height:1.25;margin:10px 0}.hero p,.hint{color:#6c687b;line-height:1.75}.panel,.result{background:white;border:1px solid #e9e4f0;border-radius:20px;padding:22px;margin:14px 0;box-shadow:0 8px 30px #45386c0a}.people{display:grid;grid-template-columns:1fr 1fr;gap:14px}.person{border:1px solid #e9e4f0;border-radius:16px;padding:15px;background:#fdfcff}.question{border-top:1px solid #eeeaf4;padding:13px 0}.question p{margin:0 0 8px;font-weight:700}.choice{display:flex;gap:9px;align-items:flex-start;font-size:14px;line-height:1.5;margin:8px 0;font-weight:400}.choice input{width:auto;margin-top:4px;accent-color:#7664a8}label{display:block;font-weight:700;font-size:14px;margin:13px 0 7px}input[type=date],input[type=time]{width:100%;padding:12px;border:1px solid #d9d3e5;border-radius:11px;font:inherit;background:#fff}button{margin-top:18px;border:0;border-radius:13px;background:#7664a8;color:#fff;font:inherit;font-weight:750;padding:15px;width:100%;cursor:pointer}.score{font-size:56px;font-weight:850;color:#7664a8;line-height:1.1}.score small{font-size:17px}.bar{height:10px;background:#eeeaf5;border-radius:99px;overflow:hidden;margin:12px 0 18px}.bar span{display:block;height:100%;background:linear-gradient(90deg,#bba9e8,#91c8df)}.cols{display:grid;grid-template-columns:1fr 1fr;gap:12px}.box{padding:14px;border-radius:14px;background:#faf8ff;border:1px solid #ece7f4;line-height:1.7}.tag{display:inline-block;background:#f2eef9;color:#594b7c;border-radius:99px;padding:6px 10px;font-size:12px;margin:3px}.list{line-height:1.8;padding-left:20px}.warning{background:#fff7e8;border:1px solid #f0ddb3;padding:12px;border-radius:12px;font-size:13px;line-height:1.7}.foot{font-size:12px;color:#6c687b;line-height:1.8;margin-top:24px}.axis{padding:8px 0;border-bottom:1px solid #eeeaf4}.back{color:#7664a8;font-weight:750;text-decoration:none}@media(max-width:650px){.people,.cols{grid-template-columns:1fr}.panel,.result{padding:16px}}
"""

def page(body, title="星と月の自動相性診断"):
    html=f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><style>{STYLE}</style></head><body><main>{body}<div class="foot">この診断は独自ルールによるエンターテインメント・自己理解用の参考結果です。科学的に検証された心理検査、関係の成功率、将来の保証ではありません。相手を決めつけず、対話のきっかけとしてご利用ください。入力内容を保存するデータベースやアカウント機能はありません。</div></main></body></html>'
    return html.encode('utf-8')

def question_html(person_key):
    chunks=[]
    for q in QUESTIONS:
        chunks.append(f'''<div class="question"><p>{q.id.upper()}｜{escape(q.prompt)}</p><label class="choice"><input type="radio" name="{person_key}_{q.id}" value="A" required><span>A. {escape(q.option_a)}</span></label><label class="choice"><input type="radio" name="{person_key}_{q.id}" value="B" required><span>B. {escape(q.option_b)}</span></label></div>''')
    return ''.join(chunks)

def form_html():
    today=date.today().isoformat()
    return f'''<section class="hero"><div class="eyebrow">MOONLIGHT × LOVE COMPATIBILITY</div><h1>ふたりの生年月日と回答から、<br>相性を自動診断。</h1><p>恋愛タイプを選ぶ必要はありません。2人が12問ずつ回答すると、16タイプを自動判定し、12キャラクター診断と合わせて相性のヒントを表示します。</p></section><form method="post"><section class="panel"><div class="people"><div class="person"><h2>あなた</h2><label for="date_a">生年月日</label><input type="date" id="date_a" name="date_a" max="{today}" required><label for="time_a">出生時刻（任意）</label><input type="time" id="time_a" name="time_a"><p class="hint">出生時刻が不明なら空欄でOK。</p></div><div class="person"><h2>お相手</h2><label for="date_b">生年月日</label><input type="date" id="date_b" name="date_b" max="{today}" required><label for="time_b">出生時刻（任意）</label><input type="time" id="time_b" name="time_b"><p class="hint">相手の時刻も任意です。</p></div></div></section><section class="panel"><h2>あなたの恋愛スタイル（12問）</h2><p class="hint">正解・不正解はありません。今の自分に近い方を選んでください。</p>{question_html('a')}</section><section class="panel"><h2>お相手の恋愛スタイル（12問）</h2><p class="hint">相手本人に回答してもらうのがおすすめです。推測で答えた場合、結果も推測ベースになります。</p>{question_html('b')}</section><button type="submit">ふたりの相性を診断する ✦</button></form>'''

def ul(items): return ''.join(f'<li>{escape(str(x))}</li>' for x in items)
def tags(items): return ''.join(f'<span class="tag">{escape(str(x))}</span>' for x in items) or '<span class="tag">なし</span>'
def get_answers(form, key): return {q.id: form.get(f'{key}_{q.id}', [''])[0] for q in QUESTIONS}
def axis_html(diag):
    return ''.join(f'<div class="axis"><b>{escape(name)}</b><br>{escape(chosen)} <span class="hint">（A {ac}票 / B {bc}票）</span></div>' for name,chosen,ac,bc in diag.axis_results)

class Handler(BaseHTTPRequestHandler):
    def send_html(self, body, status=200):
        self.send_response(status); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(body)
    def do_GET(self): self.send_html(page(form_html()))
    def do_POST(self):
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n > 100_000: raise ValueError('入力サイズが大きすぎます。')
            f=parse_qs(self.rfile.read(n).decode('utf-8'))
            da=f.get('date_a',[''])[0]; db=f.get('date_b',[''])[0]
            ta=f.get('time_a',[''])[0] or None; tb=f.get('time_b',[''])[0] or None
            if not da or not db: raise ValueError('2人分の生年月日を入力してください。')
            if date.fromisoformat(da)>date.today() or date.fromisoformat(db)>date.today(): raise ValueError('生年月日は今日以前の日付を入力してください。')
            love_a=diagnose_answers(get_answers(f,'a')); love_b=diagnose_answers(get_answers(f,'b'))
            a=make_profile('あなた',da, love_a.code, birth_time=ta)
            b=make_profile('お相手',db, love_b.code, birth_time=tb)
            r=calculate_compatibility(a,b)
            body=f'''<section class="hero"><div class="eyebrow">YOUR COMPATIBILITY</div><h1>ふたりの診断結果</h1><p>{escape(da)} × {escape(db)}</p></section><section class="result"><div class="eyebrow">REFERENCE SCORE</div><div class="score">{r.score}<small> / 100</small></div><div class="bar"><span style="width:{r.score}%"></span></div><h2>{escape(r.level)}</h2><p>{escape(r.explanation)}</p><div class="cols"><div class="box"><b>キャラクター相性（独自指標）</b><p>{r.character_score} / 100</p></div><div class="box"><b>恋愛スタイルの近さ</b><p>{r.love_type_score} / 100</p></div></div></section><section class="result"><h2>それぞれの診断結果</h2><div class="cols"><div class="box"><b>あなた</b><h3>{escape(a.character_name)}</h3><p>{escape(a.element)}・{escape(a.birth_date)}</p><h3>{escape(love_a.code)}｜{escape(love_a.name)}</h3><p>{escape(love_a.tagline)}</p><b>得意なこと</b><ul>{ul(love_a.strengths)}</ul><b>意識したいこと</b><ul>{ul(love_a.blind_spots)}</ul><p>{escape(love_a.advice)}</p><details><summary>4軸の回答結果</summary>{axis_html(love_a)}</details></div><div class="box"><b>お相手</b><h3>{escape(b.character_name)}</h3><p>{escape(b.element)}・{escape(b.birth_date)}</p><h3>{escape(love_b.code)}｜{escape(love_b.name)}</h3><p>{escape(love_b.tagline)}</p><b>得意なこと</b><ul>{ul(love_b.strengths)}</ul><b>意識したいこと</b><ul>{ul(love_b.blind_spots)}</ul><p>{escape(love_b.advice)}</p><details><summary>4軸の回答結果</summary>{axis_html(love_b)}</details></div></div></section><section class="result"><h2>共通しているところ</h2><p>{tags(r.shared_axes)}</p><ul class="list">{ul(r.attraction_points)}</ul><h2>すり合わせのヒント</h2><p>{tags(r.different_axes)}</p><ul class="list">{ul(r.friction_points)}</ul><h2>関係を育てるための提案</h2><ul class="list">{ul(r.advice)}</ul></section><section class="panel"><a class="back" href="/">← もう一度診断する</a></section>'''
            self.send_html(page(body,'相性診断結果 | 星と月'))
        except Exception as e:
            self.send_html(page(f'<section class="panel"><h1>入力を確認してください</h1><p>{escape(str(e))}</p><a class="back" href="/">戻る</a></section>'),400)
    def log_message(self, fmt, *args): print('[web]',fmt%args)

if __name__=='__main__':
    print(f'星と月 自動相性診断 v1.6: http://{HOST}:{PORT}')
    print('このサーバーはローカルPC内のみで動作します。終了は Ctrl+C')
    HTTPServer((HOST,PORT),Handler).serve_forever()
