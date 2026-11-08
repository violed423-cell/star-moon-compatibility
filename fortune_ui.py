"""Server-rendered three-mode fortune UI; no invented partner answers."""
from datetime import datetime, timedelta, timezone
from html import escape
from hashlib import sha256
from app_星月自動相性診断_v1_6 import question_html, tags, ul
from compatibility_v1_6 import ELEMENT_AFFINITY, CHAR_BY_ID
from independent_12_animal_diagnosis_v1_3 import diagnose
import fortune_content as content
import fortune_ornaments as ornaments

MODES = {'birth': ('月のめぐり', '生年月日だけ', 'ふたりの生年月日から、12キャラクターの相性を。'),
         'self': ('わたしの星', '自分だけ12問', '生年月日の相性に、あなたの恋愛スタイルを添えて。'),
         'both': ('ふたりの星座', 'ふたりで12問ずつ', 'ふたりの回答から、関係を育てるヒントを。')}
STYLE = '''
body{background:#171329;background-image:radial-gradient(ellipse at 12% 4%,#493467 0,transparent 42%),radial-gradient(ellipse at 95% 45%,#29365a 0,transparent 50%);color:#332944;min-height:100vh}main{max-width:1000px;padding:28px 20px 64px}a{color:#665080}a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid #bc8432;outline-offset:4px}.brand{display:flex;justify-content:space-between;align-items:center;color:#f6e9d6;margin:0 0 24px;gap:12px}.brand a{color:inherit;text-decoration:none;font-family:serif;font-size:23px;letter-spacing:.12em}.brand span{font-size:11px;letter-spacing:.12em}.hero{color:#fff5e9;text-align:center;padding:20px 12px 30px}.hero h1{font-family:serif;font-weight:500;line-height:1.55;font-size:clamp(28px,5vw,44px);letter-spacing:.06em}.hero p{color:#ded2ef;max-width:580px;margin:14px auto;line-height:1.9}.eyebrow{color:#ebca92;letter-spacing:.2em;font-size:11px}.sky-art{width:210px;height:130px;margin:0 auto 10px;display:block}.mode-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin:20px 0 30px}.mode-card{display:flex;flex-direction:column;min-width:0;position:relative;padding:28px 22px;border:1px solid #c5aedc;border-radius:90px 90px 22px 22px;background:linear-gradient(160deg,#fff8f0,#e9e0f7);text-align:center;text-decoration:none;color:#392c50;box-shadow:0 12px 40px #09051550}.mode-card:hover{border-color:#e5c18a;box-shadow:0 12px 40px #09051580}.mode-symbol{font-family:serif;font-size:38px;color:#83659b;margin:8px}.mode-card h2{font-family:serif;font-size:25px;margin:10px 0}.mode-card p{font-size:13px;line-height:1.8;margin:12px 0 22px}.mode-card strong{font-size:13px;color:#65517f}.mode-card .enter{margin-top:auto;border-top:1px solid #cbbcdc;padding-top:17px;font-size:13px;font-weight:700}.selection-note{color:#e2d9ed;text-align:center;font-size:13px;line-height:1.9}.panel,.result{background:#fffaf4;border:1px solid #dacbe6;box-shadow:0 12px 35px #0c081b25;border-radius:22px;padding:26px}.panel h2,.result h2{font-family:serif;letter-spacing:.04em}.person,.box{background:#f4edf8;border-color:#ded0e9}.hint,.foot{color:#665a73}.hero .hint{color:#e2d5ed}.foot{color:#c9bedb;border-top:1px solid #6c587d;padding-top:24px}.foot+a{color:#f5dfb4}.choice{padding:12px;background:#fff;border:1px solid #e2d8eb;border-radius:12px;min-height:48px}.choice:has(input:checked){background:#ece1f5;border-color:#8862a7}.choice input{flex-shrink:0;width:18px;height:18px;accent-color:#795398}.question{padding:20px 0}.question p{line-height:1.7}button,.button{background:linear-gradient(100deg,#79528e,#625088);border:1px solid #9674ad;min-height:52px}.score{color:#78568b;font-family:serif}.result>.eyebrow,.panel>.eyebrow{color:#755287}.warning{color:#604824;background:#fff2d9;border-color:#dfc591}.mode-switch{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 20px}.mode-switch a{color:#e7ddf2;font-size:13px;border:1px solid #776186;border-radius:99px;padding:11px 15px;text-decoration:none}.mode-switch a[aria-current=page]{background:#ece0f7;color:#463253}.mode-switch p{width:100%;color:#d4c6e3;font-size:12px;margin:0}.result p{line-height:1.85}.result .unknown{border:1px dashed #bca9ca;padding:15px;border-radius:14px;background:#f7f0fb}.score-note{font-size:13px;color:#665a73}.footer-nav{display:flex;gap:16px;flex-wrap:wrap;margin-top:18px}.footer-nav a{color:#e8d7b7;font-size:12px}.ornament{color:#a184b5;font-size:24px;letter-spacing:.3em;text-align:center}input[type=date],input[type=time]{min-width:0;max-width:100%;color:#342740}*{overflow-wrap:anywhere}@media(max-width:650px){main{padding:20px 16px 44px}.mode-grid{grid-template-columns:1fr;gap:16px}.mode-card{border-radius:32px;padding:20px}.mode-symbol{font-size:28px;margin:0}.mode-card h2{margin:5px 0}.mode-card p{margin:8px 0 15px}.panel,.result{padding:19px}.brand span{display:none}.hero{padding:10px 0 20px}.hero h1{font-size:29px}.sky-art{height:110px;width:180px}.score{font-size:50px}.people,.cols{grid-template-columns:1fr}}
'''
BRAND = '<header class="brand"><a href="/" aria-label="星と月 ホーム">☾ 星と月</a><span>STAR &amp; MOON · LOVE READING</span></header>'
ART = ornaments.celestial_moon()

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
    reading = content.read_birth_pair(da, db, ta, tb)
    a, b = reading.person_a, reading.person_b
    available = content.artwork_bytes() is not None
    cards = ''.join(character_card(p, label, d, available, slot) for p, label, d, slot in [(a, 'あなた', da, 'a'), (b, 'お相手', db, 'b')])
    warnings = ''.join(f'<p class="warning">{escape(label)}：{escape(w)}</p>' for p, label in [(a, 'あなた'), (b, 'お相手')] for w in p.warnings)
    extra = ''
    if love and love.answered_count:
        full = love.complete_type
        type_note = f'<h3>{escape(full.name)}</h3><p>{escape(full.tagline)}</p>' if full else ''
        extra = f'<section class="result self-supplement"><div class="eyebrow">YOUR LOVE STYLE</div><h2>あなたの恋愛スタイルに、ひとこと</h2><p class="hint">回答した{love.answered_count}問だけからの補足です。相性の％には加えていません。</p>{type_note}<ul class="list">{ul(love.statements)}</ul><p class="unknown">お相手の恋愛タイプは未診断です。答えていない質問や、お相手の気持ち・回答は推測しません。</p></section>'
    return BRAND + f'<section class="hero">{ART}<div class="eyebrow">A LITTLE MAGIC FOR TWO</div><h1>ふたりに届いた、<br>星と月のメッセージ。</h1></section>{warnings}<section class="result affinity"><div class="eyebrow">CHARACTER AFFINITY</div><h2>ふたりのキャラクター相性</h2><div class="score" data-score="{reading.score}">{reading.score}<small>%</small></div><p class="pair-explanation">{escape(reading.explanation)}</p><p class="score-note">生年月日から導く五行の組み合わせによる、独自の参考値です。関係の成功率ではありません。お相手の回答がないため、恋愛スタイルの相性・総合点は算出していません。</p></section><section class="result"><div class="eyebrow">TWO LITTLE STARS</div><h2>ふたりを表すキャラクター</h2><p class="hint">性格を決めつけるものではありません。「自分に近いかな？」と、会話のきっかけに。</p><div class="cols character-grid">{cards}</div></section>{extra}<section class="panel relationship-tips"><div class="eyebrow">A SMALL STEP TOGETHER</div><h2>関係を育てる小さなヒント</h2><ul class="list">{ul(reading.tips)}</ul></section>' + premium_cta() + '<p class="selection-note"><a class="restart" href="/">もう一度占う</a></p>'


def character_portrait(character_id, available, instance_id='preview'):
    entry = content.ARTWORK.get(character_id)
    character = CHAR_BY_ID.get(character_id)
    if not entry or not character or entry[0] != character.name or not available:
        name = character.name if character else 'キャラクター'
        return f'<div class="portrait-missing" role="img" aria-label="{escape(name)}の画像は準備中"><span aria-hidden="true">☾</span><small>画像は準備中</small></div>'
    name, (x, y, width, height) = entry
    # A viewBox alone is not a crop: meet can expose outside pixels in letterboxes.
    # Clip the image itself in source coordinates, then preserve the ROI's ratio.
    # Explicit card slots make same-character pairs unique and repeated renders stable.
    clip_id = 'portrait-clip-' + sha256(f'{instance_id}:{character_id}'.encode()).hexdigest()[:16]
    return f'<svg class="character-portrait" role="img" aria-label="{escape(name)}" viewBox="{x} {y} {width} {height}" preserveAspectRatio="xMidYMid meet"><defs><clipPath id="{clip_id}" clipPathUnits="userSpaceOnUse"><rect x="{x}" y="{y}" width="{width}" height="{height}" /></clipPath></defs><image href="{content.ARTWORK_URL}" width="1312" height="1199" clip-path="url(#{clip_id})" /></svg>'


def character_card(person, label, birth_date, available, instance_id):
    personality, thinking, _ = content.PERSONALITY[person.character_id]
    return f'<article class="box character-card" data-character="{escape(person.character_id)}"><p class="person-label">{escape(label)}</p>{character_portrait(person.character_id, available, instance_id)}<h3>{escape(person.character_name)}</h3><p class="birth-label">{escape(birth_date)}</p><p>{tags(person.keywords)}</p><p>{escape(personality)}</p><p class="thinking">{escape(thinking)}</p><p class="character-tip"><b>恋の小さなヒント</b><br>{escape(CHAR_BY_ID[person.character_id].love_advice)}。</p></article>'


def premium_cta():
    """Information only while purchase routing is on hold; no URL activation."""
    return '<section class="panel premium-cta"><div class="eyebrow">STAR &amp; MOON</div><h2>星と月の鑑定書</h2><p>ふたりの個性と関係のヒントをまとめた鑑定書を準備しています。</p><p class="sales-status">鑑定書は準備中です。販売・購入のご案内は現在行っていません。</p><p class="score-note">このサイト上で決済・購入確認・自動納品は行いません。</p></section>'


def premium_page():
    return BRAND + '<section class="hero">' + ART + '<div class="eyebrow">STAR &amp; MOON</div><h1>星と月の鑑定書</h1><p>ふたりの個性と、関係を育てるヒントを。</p></section>' + premium_cta() + '<section class="panel"><p>無料診断は、お二人の生年月日から何度でもお試しいただけます。鑑定書を購入したことにはなりません。</p><a href="/">無料診断に戻る</a><p class="hint">相手の気持ちや未来を断定するものではなく、エンターテインメント・自己理解のための読み物です。</p></section>'


def free_form():
    # Begin with the birth-only form; no questionnaire is selected by default.
    body = form('birth')
    begin = body.index('<nav class="mode-switch"')
    end = body.index('</nav>', begin) + len('</nav>')
    body = body[:begin] + body[end:]
    body = body.replace('name="mode" value="birth"', 'name="mode" value="free"')
    body = body.replace('生年月日だけ</div>', 'FREE READING</div>')
    body = body.replace('ふたりの生年月日から、12キャラクターの相性を。', 'ふたりの生年月日で占えます。あなたの12問は、答えたいときだけ。')
    optional = '<section class="panel optional-style"><h2>あなたの恋愛スタイルも見る？</h2><label class="choice"><input type="checkbox" name="include_self" value="yes" aria-controls="optional-questions"><span>自分の12問にも答える（任意）</span></label><p class="hint">チェックなしで診断できます。チェックを外すと、入力済みの回答も結果に使いません。</p><div class="optional-questions" id="optional-questions"><p class="hint">答えたい質問だけで大丈夫です。回答した分だけ短い補足を添えます。お相手の回答は不要です。</p>' + question_html('a').replace(' required', '') + '</div></section>'
    body = body.replace('<button type="submit">', optional + '<button type="submit">')
    return body

STYLE += '.optional-questions{display:none}.optional-style:has(input[name="include_self"]:checked) .optional-questions{display:block}'
STYLE += '''
.affinity{text-align:center;border-color:#cbb38b;background:linear-gradient(145deg,#fffaf2,#f4eefa)}.affinity .score{font-size:clamp(64px,12vw,90px);margin:18px 0;color:#755184}.affinity .score small{font-size:30px;margin-left:4px}.pair-explanation{font-family:serif;font-size:19px;max-width:690px;margin:20px auto}.affinity .score-note{max-width:700px;margin:16px auto 0}.character-grid{gap:20px}.character-card{padding:22px;background:linear-gradient(160deg,#fffdf8,#f1eaf6);border-color:#d8c8db}.person-label{text-align:center;letter-spacing:.12em;font-weight:700;color:#7e648b}.character-card h3{font-family:serif;text-align:center;font-size:25px;margin:14px 0 2px}.birth-label{text-align:center;font-size:12px;color:#7b6e82}.character-portrait{display:block;width:100%;height:200px;max-width:265px;margin:auto;border-radius:24px;overflow:hidden}.portrait-missing{display:flex;flex-direction:column;align-items:center;justify-content:center;height:200px;margin:auto;background:#f0e8f4;border:1px dashed #cbb9d7;border-radius:24px;color:#71587e}.portrait-missing span{font-size:44px}.portrait-missing small{font-size:12px}.character-card .tag{background:#ebe0f3}.character-card .thinking{color:#65536e;font-size:14px}.character-tip{border-top:1px solid #d9c8de;padding-top:14px;font-size:14px}.premium-cta{position:relative;overflow:hidden;text-align:center;margin-top:24px;padding:38px 30px;border:1px solid #c7a76b;box-shadow:inset 0 0 0 5px #fff9ed,inset 0 0 0 6px #e2cda9,0 12px 35px #0c081b25;background:linear-gradient(130deg,#fff3e8,#f2e8f6 65%,#e5f1f1)}.premium-cta h2{font-size:clamp(27px,4vw,36px);line-height:1.6;color:#594568;margin:15px 0}.premium-cta>p{max-width:630px;margin:16px auto;line-height:1.85}.premium-benefits{display:flex;flex-wrap:wrap;gap:9px;justify-content:center;margin:22px 0}.premium-benefits span{border:1px solid #d0b98d;background:#fffaf1;border-radius:99px;padding:7px 12px;font-size:13px;color:#806236}.premium-button{display:inline-flex;align-items:center;justify-content:center;gap:12px;color:#fff;text-decoration:none;padding:16px 25px;border-radius:14px;font-weight:700;max-width:100%}.sales-status{border:1px solid #d2bd97;border-radius:14px;padding:16px;background:#fff9ef;color:#715c3c}.restart{color:#f0d6a5}.self-supplement .list{font-size:14px}.relationship-tips .list{padding-left:22px}.relationship-tips li{margin:10px 0}@media(max-width:650px){.character-card{padding:20px}.premium-cta{padding:30px 21px}.pair-explanation{font-size:17px}.character-portrait{height:205px}.character-grid{gap:18px}}
'''
STYLE += ornaments.STYLE
