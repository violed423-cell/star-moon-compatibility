"""Original vector ornamentation for the free reading, not reference-image copies.

Decorative SVGs have no interactive targets, external resources, or document IDs.
The original character portrait renderer and its strict clipping stay separate.
"""
from math import cos, sin, pi
import re

PALETTE = {
    'ivory': '#FFFDF6', 'blue': '#E6F3F9', 'rose': '#F9E9EE',
    'lavender': '#F0EAF9', 'ink': '#47475C',
    'gold_shadow': '#9C702F', 'gold': '#BE984D', 'gold_light': '#F3DE9C',
}

CORNER_PATH = (
    'M10 94 C2 76 23 67 17 51 C12 38 18 23 33 23 '
    'C48 23 45 10 59 9 C72 7 79 17 94 10 '
    'M12 74 C31 78 41 62 31 53 C23 45 16 53 23 59 C28 62 32 57 29 54 '
    'M27 24 C31 39 44 42 50 32 C55 23 46 17 41 24 C38 28 43 32 46 29 '
    'M54 12 C57 27 72 34 79 23 C84 15 78 10 72 14 '
    'M10 94 C18 88 27 88 30 80 M18 49 C7 44 8 35 13 31 '
    'M60 10 C58 3 64 2 67 4'
)
LEAF_PATH = (
    'M17 50 C3 50 1 39 7 31 C9 40 17 39 17 50 Z '
    'M31 24 C21 15 26 5 36 5 C31 12 38 16 31 24 Z '
    'M54 13 C49 3 55 0 62 2 C57 6 60 10 54 13 Z '
    'M14 73 C26 69 28 78 23 85 C23 77 17 80 14 73 Z '
    'M78 18 C83 4 93 4 98 10 C88 9 90 18 78 18 Z'
)


def _gold_lines(path):
    return ''.join(f'<path class="{tone}" d="{path}" />' for tone in ('gold-shadow', 'gold-body', 'gold-highlight'))


CORNER = ('<svg viewBox="0 0 104 104" aria-hidden="true" focusable="false">'
          + _gold_lines(CORNER_PATH)
          + f'<path class="gold-leaf" d="{LEAF_PATH}" /></svg>')
CREST = ('<svg viewBox="0 0 180 52" aria-hidden="true" focusable="false">'
         + _gold_lines('M8 35 C25 44 38 20 53 30 C65 39 75 28 90 29 C105 28 115 39 127 30 C142 20 155 44 172 35 M53 30 C45 17 60 9 66 19 C70 27 61 30 58 24 M127 30 C135 17 120 9 114 19 C110 27 119 30 122 24 M90 29 C77 24 79 13 90 6 C101 13 103 24 90 29 M90 29 L90 42')
         + '<path class="gold-leaf" d="M90 28 C80 22 83 14 90 8 C97 14 100 22 90 28 Z M84 28 C67 26 66 13 73 12 C73 21 83 19 84 28 Z M96 28 C113 26 114 13 107 12 C107 21 97 19 96 28 Z" /></svg>')
FRAME = ('<div class="gilded-trim" aria-hidden="true">'
         + ''.join(f'<span class="gilded-corner {side}">{CORNER}</span>' for side in ('top-left', 'top-right', 'bottom-left', 'bottom-right'))
         + f'<span class="gilded-crest">{CREST}</span></div>')


def decorate_body(body):
    """Insert presentation-only trim once, leaving forms and all existing classes intact."""
    return re.sub(r'(<section class="(?:panel|result)(?: [^"]*)?")>',
                  lambda m: m[1] + ' data-ornate="true">' + FRAME, body)


def celestial_moon():
    rays = []
    for n in range(36):
        angle = (n * 10 - 90) * pi / 180
        inner, outer = (86, 99) if n % 3 == 0 else (88, 94)
        x1, y1 = 130 + inner * cos(angle), 107 + inner * sin(angle)
        x2, y2 = 130 + outer * cos(angle), 107 + outer * sin(angle)
        rays.append(f'<path d="M{x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f}" />')
    # One original closed path traces the crescent and its inward-facing profile.
    moon = ('M150 36 C121 27 91 43 79 72 C62 110 78 153 112 170 '
            'C134 181 158 179 179 167 C155 171 138 157 132 141 '
            'C128 133 129 126 135 120 C138 117 137 114 134 112 '
            'C132 111 133 108 137 107 C143 106 145 102 141 99 '
            'L134 94 C131 91 132 88 132 84 C129 66 136 47 150 36 Z')
    return ('<svg class="sky-art celestial-moon" viewBox="0 0 260 214" aria-hidden="true" focusable="false">'
            '<circle class="moon-halo" cx="130" cy="107" r="78" />'
            '<g class="celestial-lines"><circle cx="130" cy="107" r="82" />'
            '<circle cx="130" cy="107" r="75" />' + ''.join(rays) + '</g>'
            f'<path class="moon-body" d="{moon}" />'
            '<path class="moon-highlight" d="M139 40 C113 37 91 54 84 77 C73 110 87 144 111 157" />'
            '<path class="moon-face" d="M112 88 Q119 94 126 88 M113 88 L111 90 M116 91 L114 94 M122 92 L122 95 M128 118 Q133 121 137 117" />'
            '<path class="moon-star" d="M174 70 L176 77 L183 79 L176 81 L174 88 L172 81 L165 79 L172 77 Z M162 119 L163.5 124 L169 126 L163.5 128 L162 133 L160.5 128 L155 126 L160.5 124 Z" />'
            '<g class="celestial-dots"><circle cx="183" cy="111" r="2" /><circle cx="157" cy="61" r="1.5" /><circle cx="172" cy="145" r="1.5" /></g></svg>')


STYLE = '''
:root{--ivory:#FFFDF6;--pastel-blue:#E6F3F9;--pastel-rose:#F9E9EE;--pastel-lavender:#F0EAF9;--ink:#47475C;--gold-shadow:#9C702F;--gold:#BE984D;--gold-light:#F3DE9C}
body{color:var(--ink);background-color:var(--ivory);background-image:radial-gradient(ellipse at 7% 0%,#E6F3F9 0,transparent 45%),radial-gradient(ellipse at 96% 18%,#F9E9EE 0,transparent 44%),linear-gradient(180deg,#F0EAF930,#FFFDF6 72%)}
main{max-width:1000px;padding-top:24px}.brand{color:#796244;margin-bottom:8px}.brand a{font-size:22px}.brand span{color:#8B7B8F}.hero{color:#5F506B;padding:8px 14px 26px}.hero h1{color:#62516E;letter-spacing:.05em;font-size:clamp(29px,4.7vw,43px);font-family:"Yu Mincho","Hiragino Mincho ProN",serif}.hero p{color:#70657B}.hero .eyebrow,.eyebrow{color:#8F6A32}.hero .hint{color:#70657B}.sky-art{width:224px;height:184px;margin:0 auto 4px;filter:drop-shadow(0 4px 5px #9C702F15)}
.celestial-lines{fill:none;stroke:var(--gold);stroke-width:.8;opacity:.76}.moon-halo{fill:#FFFDF6;fill-opacity:.55}.moon-body{fill:#ECD59A;stroke:var(--gold-shadow);stroke-width:1.35;stroke-linejoin:round}.moon-highlight{fill:none;stroke:#FFF6D5;stroke-width:3;stroke-linecap:round;opacity:.9}.moon-face{fill:none;stroke:#89612D;stroke-width:1.3;stroke-linecap:round}.moon-star,.celestial-dots{fill:var(--gold)}
.panel,.result{position:relative;isolation:isolate;background:linear-gradient(135deg,#FFFDF6,#FFFFFF 70%);border:1px solid #D7BD8940;border-radius:46px 40px 48px 42px;padding:40px 35px 34px;margin:27px 0;box-shadow:0 12px 32px #85709512}.panel h2,.result h2{color:#62516E;font-family:"Yu Mincho","Hiragino Mincho ProN",serif}.panel[data-ornate]::before,.result[data-ornate]::before{content:"";position:absolute;inset:8px;pointer-events:none;z-index:0;border:1px solid #BE984D75;border-radius:40px 35px 42px 36px / 34px 42px 35px 44px}.panel[data-ornate]::after,.result[data-ornate]::after{content:"";position:absolute;inset:13px;pointer-events:none;z-index:0;border:1px solid #F3DE9C90;border-radius:35px 31px 38px 33px / 30px 38px 31px 40px}.panel[data-ornate]>*:not(.gilded-trim),.result[data-ornate]>*:not(.gilded-trim){position:relative;z-index:1}
.gilded-trim{position:absolute;inset:0;pointer-events:none;user-select:none;z-index:2}.gilded-trim svg{display:block;width:100%;height:100%;overflow:visible}.gilded-corner{position:absolute;width:82px;height:82px}.gilded-corner.top-left{top:1px;left:1px}.gilded-corner.top-right{top:1px;right:1px;transform:scaleX(-1)}.gilded-corner.bottom-left{bottom:1px;left:1px;transform:scaleY(-1)}.gilded-corner.bottom-right{bottom:1px;right:1px;transform:scale(-1)}.gilded-crest{position:absolute;left:50%;top:-17px;transform:translateX(-50%);width:164px;height:47px}.gold-shadow,.gold-body,.gold-highlight{fill:none;stroke-linejoin:round;stroke-linecap:round}.gold-shadow{stroke:var(--gold-shadow);stroke-width:3.8}.gold-body{stroke:var(--gold);stroke-width:2.7}.gold-highlight{stroke:var(--gold-light);stroke-width:.85}.gold-leaf{fill:var(--gold-light);stroke:var(--gold);stroke-width:1}
.person,.box{background:linear-gradient(150deg,#F0EAF965,#E6F3F94F);border-color:#CFC4DA}.person{border-radius:24px;padding:18px}.choice{border-color:#D8D0E1;background:#FFFDFB}.choice:has(input:checked){background:#EFE6F7;border-color:#9776AA}.hint,.score-note{color:#6D6378}.selection-note{color:#73677D}.foot{color:#756A7C;border-top-color:#D8C8A7}.footer-nav a{color:#77603B}.mode-switch a{color:#6C5A78;border-color:#CBB7D7}.mode-switch p{color:#74647F}.warning{background:#FFF8E7;border-color:#DDC89E;color:#71552D}.result>.eyebrow,.panel>.eyebrow{color:#8F6A32;text-align:center}.affinity{background:linear-gradient(140deg,#FFF9EE,#F0EAF9 72%,#E6F3F9)}.affinity .score{color:#826394;text-shadow:0 2px 0 #FFFDF6}.affinity .pair-explanation{color:#62526D}.character-card{background:linear-gradient(140deg,#FFFDF6,#F9E9EE60 45%,#E6F3F96B);border:1px solid #D4BC8A;border-radius:34px 34px 25px 25px;padding:23px}.character-card h3{color:#62516E}.character-card .tag{background:#F0EAF9;border:1px solid #D5C7E0}.character-card .thinking{color:#6D6378}.character-tip{border-top-color:#D5C29A}.character-portrait{background:#FFFDF6}.portrait-missing{background:linear-gradient(145deg,#F0EAF9,#E6F3F9);border-color:#C8B389}.person-label{color:#937243}.premium-cta{overflow:visible;border:1px solid #D7BD8940;border-radius:46px 40px 48px 42px;padding:42px 35px 34px;background:linear-gradient(130deg,#FFF8E9,#F9E9EE 45%,#F0EAF9 78%,#E6F3F9);box-shadow:0 12px 32px #85709516}.premium-cta h2{color:#62516E}.premium-benefits span{background:#FFFDF6;border-color:#D5BE8D;color:#826337}.sales-status{background:#FFFDF6B3;border-color:#D9C394;color:#77603B}button,.button{border:1px solid #BCA371;background:linear-gradient(110deg,#836397,#6C5488);box-shadow:0 4px 12px #6C54881A}button:hover,.button:hover{background:linear-gradient(110deg,#77578B,#60467C)}a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid #8D672B;outline-offset:4px}.restart{color:#77603B}.self-supplement .unknown{background:#F0EAF966;border-color:#C9B7D5}
@media(max-width:650px){main{padding:16px 14px 40px}.brand{margin-bottom:5px}.brand a{font-size:21px}.hero{padding:2px 6px 18px}.hero h1{font-size:29px;line-height:1.5}.hero p{font-size:14px;margin:10px auto;line-height:1.75}.sky-art{width:158px;height:130px;margin:0 auto}.panel,.result{padding:35px 23px 29px;margin:24px 0;border-radius:35px 31px 37px 32px}.panel[data-ornate]::before,.result[data-ornate]::before{inset:6px;border-radius:30px 26px 32px 27px}.panel[data-ornate]::after,.result[data-ornate]::after{inset:10px;border-radius:26px 22px 28px 23px}.gilded-corner{width:63px;height:63px}.gilded-crest{width:136px;height:39px;top:-14px}.panel h2,.result h2{font-size:22px;line-height:1.6}.person{padding:15px;border-radius:20px}.people,.cols{grid-template-columns:1fr}.character-card{padding:19px;border-radius:29px 29px 23px 23px}.character-card h3{font-size:23px}.premium-cta{padding:37px 24px 30px}.premium-cta h2{font-size:28px}.premium-button{width:100%;padding:14px;font-size:14px}.premium-benefits{gap:6px}.premium-benefits span{font-size:12px;padding:6px 9px}.footer-nav{gap:13px}.pair-explanation{font-size:17px}.affinity .score{font-size:70px}.affinity .score small{font-size:27px}}
@media(max-width:360px){main{padding-left:10px;padding-right:10px}.panel,.result{padding-left:19px;padding-right:19px}.person{padding:12px}.hero h1{font-size:27px}.brand a{font-size:20px}.gilded-corner{width:56px;height:56px}}
'''
