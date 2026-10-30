"""Server-rendered three-mode fortune UI; no invented partner answers."""
from datetime import datetime, timedelta, timezone
from html import escape
from app_星月自動相性診断_v1_6 import question_html, tags, ul
from compatibility_v1_6 import ELEMENT_AFFINITY, CHAR_BY_ID
from independent_12_animal_diagnosis_v1_3 import diagnose

MODES = {'birth': ('月のめぐり', '生年月日だけ', 'ふたりの生年月日から、12キャラクターの相性を。'),
         'self': ('わたしの星', '自分だけ12問', '生年月日の相性に、あなたの恋愛スタイルを添えて。'),
         'both': ('ふたりの星座', 'ふたりで12問ずつ', 'ふたりの回答から、関係を育てるヒントを。')}
STYLE = '''
body{background:#171329;background-image:radial-gradient(ellipse at 12% 4%,#493467 0,transparent 42%),radial-gradient(ellipse at 95% 45%,#29365a 0,transparent 50%);color:#332944;min-height:100vh}main{max-width:1000px;padding:28px 20px 64px}a{color:#665080}a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid #bc8432;outline-offset:4px}.brand{display:flex;justify-content:space-between;align-items:center;color:#f6e9d6;margin:0 0 24px;gap:12px}.brand a{color:inherit;text-decoration:none;font-family:serif;font-size:23px;letter-spacing:.12em}.brand span{font-size:11px;letter-spacing:.12em}.hero{color:#fff5e9;text-align:center;padding:20px 12px 30px}.hero h1{font-family:serif;font-weight:500;line-height:1.55;font-size:clamp(28px,5vw,44px);letter-spacing:.06em}.hero p{color:#ded2ef;max-width:580px;margin:14px auto;line-height:1.9}.eyebrow{color:#ebca92;letter-spacing:.2em;font-size:11px}.sky-art{width:210px;height:130px;margin:0 auto 10px;display:block}.mode-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin:20px 0 30px}.mode-card{display:flex;flex-direction:column;min-width:0;position:relative;padding:28px 22px;border:1px solid #c5aedc;border-radius:90px 90px 22px 22px;background:linear-gradient(160deg,#fff8f0,#e9e0f7);text-align:center;text-decoration:none;color:#392c50;box-shadow:0 12px 40px #09051550}.mode-card:hover{border-color:#e5c18a;box-shadow:0 12px 40px #09051580}.mode-symbol{font-family:serif;font-size:38px;color:#83659b;margin:8px}.mode-card h2{font-family:serif;font-size:25px;margin:10px 0}.mode-card p{font-size:13px;line-height:1.8;margin:12px 0 22px}.mode-card strong{font-size:13px;color:#65517f}.mode-card .enter{margin-top:auto;border-top:1px solid #cbbcdc;padding-top:17px;font-size:13px;font-weight:700}.selection-note{color:#e2d9ed;text-align:center;font-size:13px;line-height:1.9}.panel,.result{background:#fffaf4;border:1px solid #dacbe6;box-shadow:0 12px 35px #0c081b25;border-radius:22px;padding:26px}.panel h2,.result h2{font-family:serif;letter-spacing:.04em}.person,.box{background:#f4edf8;border-color:#ded0e9}.hint,.foot{color:#665a73}.hero .hint{color:#e2d5ed}.foot{color:#c9bedb;border-top:1px solid #6c587d;padding-top:24px}.foot+a{color:#f5dfb4}.choice{padding:12px;background:#fff;border:1px solid #e2d8eb;border-radius:12px;min-height:48px}.choice:has(input:checked){background:#ece1f5;border-color:#8862a7}.choice input{flex-shrink:0;width:18px;height:18px;accent-color:#795398}.question{padding:20px 0}.question p{line-height:1.7}button,.button{background:linear-gradient(100deg,#79528e,#625088);border:1px solid #9674ad;min-height:52px}.score{color:#78568b;font-family:serif}.result>.eyebrow,.panel>.eyebrow{color:#755287}.warning{color:#604824;background:#fff2d9;border-color:#dfc591}.mode-switch{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 20px}.mode-switch a{color:#e7ddf2;font-size:13px;border:1px solid #776186;border-radius:99px;padding:11px 15px;text-decoration:none}.mode-switch a[aria-current=page]{background:#ece0f7;color:#463253}.mode-switch p{width:100%;color:#d4c6e3;font-size:12px;margin:0}.result p{line-height:1.85}.result .unknown{border:1px dashed #bca9ca;padding:15px;border-radius:14px;background:#f7f0fb}.score-note{font-size:13px;color:#665a73}.footer-nav{display:flex;gap:16px;flex-wrap:wrap;margin-top:18px}.footer-nav a{color:#e8d7b7;font-size:12px}.ornament{color:#a184b5;font-size:24px;letter-spacing:.3em;text-align:center}input[type=date],input[type=time]{min-width:0;max-width:100%;color:#342740}*{overflow-wrap:anywhere}@media(max-width:650px){main{padding:20px 16px 44px}.mode-grid{grid-template-columns:1fr;gap:16px}.mode-card{border-radius:32px;padding:20px}.mode-symbol{font-size:28px;margin:0}.mode-card h2{margin:5px 0}.mode-card p{margin:8px 0 15px}.panel,.result{padding:19px}.brand span{display:none}.hero{padding:10px 0 20px}.hero h1{font-size:29px}.sky-art{height:110px;width:180px}.score{font-size:50px}.people,.cols{grid-template-columns:1fr}}
'''
ART = '''<svg class="sky-art" viewBox="0 0 240 150" aria-hidden="true"><g fill="none" stroke="#bda5d6" stroke-width="1"><path d="M15 104 53 63 87 85 131 30 185 70 222 44" opacity=".65"/><circle cx="120" cy="77" r="60" opacity=".25"/><ellipse cx="120" cy="77" rx="94" ry="34" transform="rotate(-18 120 77)" opacity=".3"/></g><path d="M145 31a47 47 0 1 0 15 82 43 43 0 0 1-15-82" fill="#f0d9ab"/><g fill="#f4d8a8"><circle cx="15" cy="104" r="3"/><circle cx="53" cy="63" r="3"/><circle cx="87" cy="85" r="2"/><circle cx="185" cy="70" r="3"/><path d="m222 37 2 5 5 2-5 2-2 5-2-5-5-2 5-2z"/><path d="m131 21 2 6 6 3-6 2-2 6-2-6-6-2 6-3z"/></g></svg>'''
BRAND = '<header class="brand"><a href="/" aria-label="星と月 ホーム">☾ 星と月</a><span>STAR &amp; MOON · LOVE READING</span></header>'

def landing():
    cards=''.join(f'<a class="mode-card" href="/{key}"><span class="mode-symbol" aria-hidden="true">{symbol}</span><strong>0{i} · {escape(meta[1])}</strong><h2>{escape(meta[0])}</h2><p>{escape(meta[2])}</p><span class="enter">この占いをはじめる →</span></a>' for i,(key,meta),symbol in zip(range(1,4),MODES.items(),('☾','✧','✦')))
    return BRAND+f'<section class="hero">{ART}<div class="eyebrow">A LITTLE MAGIC FOR TWO</div><h1>星をたどって、<br>ふたりの物語を。</h1><p>ふたりの生年月日からひもとく、星と月の12キャラクター。<br>いま知りたいことに合わせて、3つの扉からどうぞ。</p></section><div class="mode-grid">{cards}</div><p class="selection-note">質問なしでも、自分だけでも、ふたりでも。<br>相手の答えが分からないとき、想像で埋めなくて大丈夫。</p>'

def form(mode):
    meta=MODES[mode]; today=datetime.now(timezone(timedelta(hours=9))).date().isoformat()
    switch='<nav class="mode-switch" aria-label="診断方法">'+''.join(f'<a href="/{key}"'+(' aria-current="page"' if key==mode else '')+f'>{escape(m[1])}</a>' for key,m in MODES.items())+'<p>方法を切り替えると入力はリセットされます。入力内容はURLに含めません。</p></nav>'
    people=''.join(f'<div class="person"><h2>{label}</h2><label for="date_{key}">生年月日</label><input type="date" id="date_{key}" name="date_{key}" min="1900-01-01" max="{today}" required><label for="time_{key}">出生時刻（任意）</label><input type="time" id="time_{key}" name="time_{key}"><p class="hint">分からないときは空欄で大丈夫です。</p></div>' for key,label in [('a','あなた'),('b','お相手')])
    questions=''
    for key,label in ([('a','あなた')] if mode=='self' else [('a','あなた'),('b','お相手')] if mode=='both' else []):
        questions+=f'<section class="panel"><div class="eyebrow">LOVE STYLE · 12 QUESTIONS</div><h2>{label}の恋愛スタイル（12問）</h2><p class="hint">'+('お相手本人が回答してください。分からない場合は「自分だけ12問」をお選びください。' if key=='b' else '正解はありません。今の自分に近い方を選んでください。')+f'</p>{question_html(key)}</section>'
    return BRAND+f'<section class="hero">{ART}<div class="eyebrow">{escape(meta[1])}</div><h1>{escape(meta[0])}</h1><p>{escape(meta[2])}</p></section>'+switch+f'<form method="post"><input type="hidden" name="mode" value="{mode}"><section class="panel"><h2>ふたりの生年月日</h2><div class="people">{people}</div></section>{questions}<button type="submit">星と月のメッセージを受け取る ✦</button></form>'

def partial_result(mode, da, db, ta, tb, love=None):
    a,b=diagnose(da,ta),diagnose(db,tb)
    score=round(ELEMENT_AFFINITY.get(frozenset((a.element,b.element)),12)/20*100)
    cards=''.join(f'<div class="box"><div class="ornament" aria-hidden="true">☾ ✧</div><b>{label}</b><h3>{escape(p.character_name)}</h3><p>{escape(p.element)}・{escape(d)}</p><p>{tags(p.keywords)}</p><p>{escape(CHAR_BY_ID[p.character_id].love_advice)}</p></div>' for p,label,d in [(a,'あなた',da),(b,'お相手',db)])
    warnings=''.join(f'<p class="warning">{escape(w)}</p>' for p in (a,b) for w in p.warnings)
    extra=f'<section class="result"><div class="eyebrow">YOUR LOVE STYLE</div><h2>あなたの恋愛スタイル</h2><h3>{escape(love.name)} · {escape(love.code)}</h3><p>{escape(love.tagline)}</p><ul>{ul(love.strengths)}</ul><p>{escape(love.advice)}</p><p class="unknown">お相手の恋愛タイプは未診断です。あなたの回答だけから相手の気持ち・タイプや、ふたりの恋愛スタイル相性は判定しません。</p></section>' if love else ''
    return BRAND+f'<section class="hero">{ART}<div class="eyebrow">{escape(MODES[mode][0])}</div><h1>ふたりに届いた、<br>星と月のメッセージ。</h1></section>{warnings}<section class="result"><div class="eyebrow">CHARACTER AFFINITY</div><h2>12キャラクターの相性</h2><div class="score">{score}<small> / 100</small></div><p class="score-note">五行の組み合わせによる独自の参考値です。恋愛スタイルの相性・総合点は未算出。今後提供予定の「ふたりで12問ずつ」の総合点とは計算方法が異なり、直接比較できません。</p><div class="cols">{cards}</div></section>{extra}<section class="panel"><h2>関係を育てる小さなヒント</h2><p>この結果をきっかけに、「どんな時間が心地いい？」と聞いてみてください。答え合わせより、ふたりの言葉を大切に。</p><a href="/">もう一度占う</a> · <a href="/premium">ふたりの詳しい診断（準備中）</a></section>'


def free_form():
    # Begin with the birth-only form; no questionnaire is selected by default.
    body = form('birth')
    begin = body.index('<nav class="mode-switch"')
    end = body.index('</nav>', begin) + len('</nav>')
    body = body[:begin] + body[end:]
    body = body.replace('name="mode" value="birth"', 'name="mode" value="free"')
    body = body.replace('生年月日だけ</div>', 'FREE READING</div>')
    body = body.replace('ふたりの生年月日から、12キャラクターの相性を。', 'ふたりの生年月日で占えます。あなたの12問は、答えたいときだけ。')
    optional = '<section class="panel optional-style"><h2>あなたの恋愛スタイルも見る？</h2><label class="choice"><input type="checkbox" name="include_self" value="yes"><span>自分の12問にも答える（任意）</span></label><p class="hint">チェックなしで診断できます。チェックを外すと、入力済みの回答も結果に使いません。</p><div class="optional-questions"><p class="hint">選んだ場合は12問すべてに回答してください。お相手の回答は不要です。</p>' + question_html('a').replace(' required', '') + '</div></section>'
    body = body.replace('<button type="submit">', optional + '<button type="submit">')
    return body

STYLE += '.optional-questions{display:none}.optional-style:has(input[name="include_self"]:checked) .optional-questions{display:block}'
