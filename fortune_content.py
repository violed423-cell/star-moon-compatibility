"""Free reading presentation, without changing the existing diagnostic rules.

Artwork IDs are mapped by name, never by element color or tuple position.
No payment state, partner answers, contact forms, or delivery automation live here.
"""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from compatibility_v1_6 import CHAR_BY_ID, ELEMENT_AFFINITY
from independent_12_animal_diagnosis_v1_3 import Diagnosis, diagnose
from love_type_16_v1_4 import AXES, QUESTIONS, LoveDiagnosis, diagnose_answers

ARTWORK_PATH = Path(__file__).with_name('assets') / 'characters-source.jpeg'
ARTWORK_SHA256 = '9ee979ce972b46e9da83221b7c905eeafb258720a642efd39639b80520eee115'
ARTWORK_SIZE = (1312, 1199)
ARTWORK_URL = '/assets/characters-source.jpeg'
# Explicit source-image name + ROI; source order does not equal engine order.
ARTWORK = {
    'stardew_rabbit': ('星雫の月兎', (19, 193, 186, 165)),
    'moonlight_fox': ('月灯りの白狐', (348, 193, 151, 163)),
    'sunshine_lion': ('陽だまりの獅子', (675, 192, 159, 165)),
    'violet_cat': ('紫宵の星猫', (1003, 193, 151, 164)),
    'star_bear': ('星読みの小熊', (21, 507, 182, 177)),
    'seabreeze_dragon': ('海風の星龍', (348, 507, 184, 177)),
    'forest_fawn': ('森隠れの子鹿', (678, 508, 185, 178)),
    'sunrise_phoenix': ('朝焼けの鳳凰', (1006, 507, 174, 178)),
    'moonsea_otter': ('月海のラッコ', (20, 836, 234, 147)),
    'moonowl': ('月翔けのフクロウ', (349, 835, 226, 147)),
    'watermirror_unicorn': ('水鏡のユニコーン', (679, 836, 226, 147)),
    'star_squirrel': ('星の実りのリス', (1006, 837, 218, 148)),
}

# Plain-language interpretations of this product's existing character keywords.
# These are fictional reading prompts, not claims about a person's actual mind.
PERSONALITY = {
    'stardew_rabbit': ('小さな気持ちの変化に目を向け、そっと寄り添う月兎。相手が安心できる空気を大切にするキャラクターです。', '「どう感じるだろう」と相手の立場から考える一方、自分の希望を後回しにしやすい、という読み方ができます。', '気持ちへの細やかな共感'),
    'moonlight_fox': ('会話の流れや場の空気を読み、新しい考えも柔らかく取り入れる白狐。知性と直感を行き来するキャラクターです。', 'すぐに一つの答えに決めず、いくつかの可能性を比べて考える姿を表します。伝わるのを待つより、短い言葉で希望を添えて。', '柔軟に見方を変える力'),
    'sunshine_lion': ('心が動いたら一歩を踏み出し、周りにも明るさを分ける獅子。情熱を行動につなげるキャラクターです。', '「まずやってみよう」と考える姿を表します。提案するときに相手の気分も確かめると、その明るさを一緒に楽しめそう。', '前向きに一歩を踏み出す力'),
    'violet_cat': ('好きなものや自分の感覚を大切にし、自然体で人をひきつける星猫。自由さと独立心を持つキャラクターです。', '周りの正解より「自分はどう感じるか」を頼りにする姿を表します。一人の時間が必要なときは、次に話す時間も添えると安心に。', '自分らしさを大切にする感性'),
    'star_bear': ('小さな約束を丁寧に積み重ね、身近な人を静かに支える小熊。安定と誠実さを大切にするキャラクターです。', '目先の勢いだけでなく「続けられるだろうか」と考える姿を表します。慎重さに小さな希望の言葉を添えると、関係も動きやすくなります。', '日々の信頼を積み重ねる力'),
    'seabreeze_dragon': ('まだ知らない景色や考え方に心を開き、変化を楽しむ星龍。好奇心と柔軟さを持つキャラクターです。', '一つの形に縛られず「ほかにも方法があるかも」と考える姿を表します。自由な予定にも、二人で楽しむ時間を残してみて。', '新しい可能性を見つける好奇心'),
    'forest_fawn': ('相手の気持ちを尊重し、みんなが穏やかに過ごせる場所を探す子鹿。優しさと調和を大切にするキャラクターです。', '「どちらも無理をしない方法」を考える姿を表します。合わせ続ける前に、小さな困りごとから話してみるとよさそう。', '違う気持ちをつなぐ優しさ'),
    'sunrise_phoenix': ('新しい始まりに希望を見つけ、人と一緒に楽しみを広げる鳳凰。前向きさと社交性を持つキャラクターです。', '難しいときも「ここから何ができるか」を考える姿を表します。元気な日だけでなく、疲れた日の本音も共有してみて。', '新しい楽しみを広げる明るさ'),
    'moonsea_otter': ('一緒に過ごす何気ない時間にぬくもりを見つけるラッコ。安心と身近な愛情を大切にするキャラクターです。', '「ここでほっとできるか」を大事にする姿を表します。いつもの心地よさに小さな新体験を加えると、楽しみが増えそう。', '心地よい時間を育てるぬくもり'),
    'moonowl': ('一歩引いて物事を眺め、細かな違いや背景を見つけるフクロウ。洞察と落ち着きを持つキャラクターです。', 'すぐに反応するより「なぜそうなったのか」を整理する姿を表します。考えがまとまる前でも、今の気持ちを一言伝えてみて。', '物事を落ち着いて見つめる洞察'),
    'watermirror_unicorn': ('心に描いた大切な景色を守り、関係の中にロマンを見つけるユニコーン。純粋さと理想を持つキャラクターです。', '「こんな関係でありたい」という願いから考える姿を表します。理想を分かち合いながら、今日うれしかったことも見つけてみて。', '大切な理想を描く感性'),
    'star_squirrel': ('目の前のことにこつこつ取り組み、小さな成長を喜ぶリス。努力と誠実さを大切にするキャラクターです。', '「今できることを少しずつ」と考える姿を表します。相手のために頑張る日にも、自分の休息や希望を忘れずに。', 'こつこつ関係を育てる誠実さ'),
}

def artwork_bytes():
    """Only serve the approved source bytes. Missing/unverified bytes fail closed."""
    try:
        if ARTWORK_PATH.stat().st_size != 840342:
            return None
        data = ARTWORK_PATH.read_bytes()
    except OSError:
        return None
    return data if sha256(data).hexdigest() == ARTWORK_SHA256 else None


def coconala_product_url():
    """Purchase routing is on hold pending platform guidance and user approval.

    Existing environment values are intentionally ignored. Supplying a URL must
    not enable links. Resuming this task requires a separately authorized change.
    """
    return None


@dataclass(frozen=True)
class BirthPairReading:
    person_a: Diagnosis
    person_b: Diagnosis
    score: int
    explanation: str
    tips: tuple[str, ...]


def read_birth_pair(date_a, date_b, time_a=None, time_b=None):
    """Return existing character identities and exactly the existing free score."""
    a, b = diagnose(date_a, time_a), diagnose(date_b, time_b)
    score = round(ELEMENT_AFFINITY.get(frozenset((a.element, b.element)), 12) / 20 * 100)
    # Stable order makes interpretation and score invariant under pair reversal.
    first, second = sorted((a, b), key=lambda p: p.character_id)
    if first.character_id == second.character_id:
        intro = f'{first.character_name}同士は、{PERSONALITY[first.character_id][2]}を重ねて読む組み合わせ。'
    else:
        intro = f'{first.character_name}の「{PERSONALITY[first.character_id][2]}」と、{second.character_name}の「{PERSONALITY[second.character_id][2]}」が出会う組み合わせ。'
    if score >= 90:
        summary = '異なる良さを持ち寄り、支え合うきっかけを見つけやすい、という読み方です。'
        tip = 'それぞれが得意なことと、助けてほしいことを一つずつ伝えてみましょう。'
    elif a.element == b.element:
        summary = '大切にする感覚に共通点を見つけやすい、という読み方です。似ているからこそ、言わなくても分かると決めつけないことが鍵。'
        tip = '「同じだと思っていたけれど違うことはある？」と、心地よい過ごし方を確かめてみましょう。'
    else:
        summary = '優先したいことの違いを、ゆっくり知るほど楽しみが増える、という読み方です。点数は関係の良し悪しや成功率を決めるものではありません。'
        tip = '意見が違うときは、結論を急がず「何を大事にしたい？」を先に聞いてみましょう。'
    tips = (tip, '次に一緒に過ごす時間について、二人が無理なく楽しめる小さな約束を一つ決めてみてください。')
    return BirthPairReading(a, b, score, intro + summary, tips)


@dataclass(frozen=True)
class SelfSupplement:
    answered_count: int
    statements: tuple[str, ...]
    complete_type: LoveDiagnosis | None = None


def read_self_answers(answers):
    """Only answered questions contribute. Missing answers never become A/B."""
    valid = {}
    for q in QUESTIONS:
        answer = answers.get(q.id, '')
        if answer not in ('', 'A', 'B'):
            raise ValueError('恋愛スタイルの回答は、表示されている選択肢から選んでください。')
        if answer:
            valid[q.id] = answer
    notes = []
    for axis, (name, a_label, b_label) in enumerate(AXES):
        selected = [valid[q.id] for q in QUESTIONS if q.axis == axis and q.id in valid]
        if not selected:
            continue
        a_count, b_count = selected.count('A'), selected.count('B')
        if a_count == b_count:
            text = f'{name}：今回答えた範囲では、二つの考え方を同じくらい選んでいます。'
        else:
            label = a_label if a_count > b_count else b_label
            text = f'{name}：今回答えた範囲では「{label}」を大切にしています。'
        notes.append(text)
    full_type = diagnose_answers(valid) if len(valid) == len(QUESTIONS) else None
    return SelfSupplement(len(valid), tuple(notes), full_type)
