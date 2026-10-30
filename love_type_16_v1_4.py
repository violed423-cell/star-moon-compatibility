"""Original 16-type relationship-style questionnaire for the 12-character project.

The names, descriptions, questions, and scoring here are original project material.
This is a self-reflection/entertainment questionnaire, not a validated psychological test.
"""
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class Question:
    id: str
    axis: int
    prompt: str
    option_a: str
    option_b: str

@dataclass(frozen=True)
class LoveType:
    code: str
    name: str
    tagline: str
    strengths: tuple[str, ...]
    blind_spots: tuple[str, ...]
    advice: str

AXES = (
    ("距離の縮め方", "自分からきっかけを作る", "相手の様子を見ながら進める"),
    ("愛情の伝え方", "言葉で気持ちを伝える", "行動で気持ちを示す"),
    ("恋のペース", "安心と安定を大切にする", "新鮮さと刺激を大切にする"),
    ("心地よい距離", "一緒に過ごす時間を重視する", "自分の時間も大切にする"),
)
QUESTIONS = (
    Question("q1",0,"気になる人ができたら？","自分から話しかける","相手の反応を見てから動く"),
    Question("q2",0,"連絡が途切れたときは？","自分から自然に連絡する","相手から来るか少し待つ"),
    Question("q3",0,"デートに誘うなら？","行きたい場所を提案する","相手の希望を聞いてから決める"),
    Question("q4",1,"好きな気持ちを伝えるなら？","言葉ではっきり伝えたい","行動や気遣いで伝えたい"),
    Question("q5",1,"相手が落ち込んでいるときは？","励ましや共感を言葉にする","そばにいる・手伝うなど行動する"),
    Question("q6",1,"記念日でうれしいのは？","気持ちのこもったメッセージ","準備してくれた行動や時間"),
    Question("q7",2,"理想の恋愛に近いのは？","穏やかで予測しやすい関係","新しい体験が多い関係"),
    Question("q8",2,"休日のデートは？","いつものお気に入りを楽しむ","初めての場所や体験を試す"),
    Question("q9",2,"関係が落ち着いてきたら？","安心できる日常を深めたい","新しい楽しみを一緒に探したい"),
    Question("q10",3,"恋人との時間は？","できるだけ一緒に過ごしたい","一人の時間も確保したい"),
    Question("q11",3,"予定を立てるときは？","二人の予定を中心に考える","それぞれの予定も尊重したい"),
    Question("q12",3,"連絡頻度については？","こまめにやり取りすると安心","必要なときに話せれば十分"),
)

# Code order follows the four axes above. 0 means option A majority; 1 means B majority.
_TYPES = {
 "0000": ("まっすぐな星灯り", "気持ちを伝え、安心できる関係を育てる", ("素直な愛情表現", "継続して向き合う力"), ("相手にも同じ熱量を求めがち",), "気持ちを伝えたら、相手のペースや返事を待つ余白も作ろう。"),
 "0001": ("自由を照らす星", "自分から動きながら、互いの時間も尊重する", ("行動力", "自立した関係づくり"), ("平気なふりをして寂しさを隠す",), "自由を大切にすることと、気持ちを共有することを両立させよう。"),
 "0010": ("安らぎの語り手", "言葉を交わしながら、穏やかな日常を楽しむ", ("対話力", "安心感を作る力"), ("変化を避けすぎることがある",), "小さな新しい体験を二人で試すと、安定した関係に彩りが加わる。"),
 "0011": ("風まかせの語り手", "言葉でつながりつつ、自由な余白も大切にする", ("柔らかな対話", "距離感の調整"), ("本音を話しただけで伝わったと思いがち",), "大切な話は、言葉だけでなく次の行動も一緒に決めよう。"),
 "0100": ("行動で守る灯", "行動で愛情を示し、安定した関係を築く", ("頼もしさ", "実務的な気遣い"), ("気持ちを説明するのが後回しになりやすい",), "してあげたことに加えて、なぜ大切なのかも言葉にしてみよう。"),
 "0101": ("自由を愛する守り手", "行動で支えながら、互いの自立も守る", ("さりげない支援", "相手を縛らない姿勢"), ("相手が気づいてくれると期待しやすい",), "してほしいこと・してあげたいことを、短い言葉で確認しよう。"),
 "0110": ("ぬくもりの冒険家", "行動で支えつつ、二人の新鮮な体験を楽しむ", ("一緒に挑戦する力", "気配り"), ("楽しさを優先して話し合いを先延ばしにしがち",), "楽しい予定だけでなく、お金や時間の使い方も一緒に相談しよう。"),
 "0111": ("軽やかな冒険家", "行動力と自由さで、関係に新しい風を運ぶ", ("フットワーク", "自立心"), ("連絡や説明が少なくなりやすい",), "予定が変わるときは一言共有するだけでも安心につながる。"),
 "1000": ("恋を育てる案内人", "慎重に距離を縮め、言葉と安定を大切にする", ("相手をよく見る力", "誠実な対話"), ("考えすぎて機会を逃しやすい",), "完璧なタイミングを待たず、小さな好意から伝えてみよう。"),
 "1001": ("自立を尊ぶ案内人", "慎重さと対話で、無理のない距離を作る", ("相手への配慮", "境界線を尊重する力"), ("遠慮しすぎて希望を伝えない",), "相手を尊重するのと同じくらい、自分の希望も大切にしよう。"),
 "1010": ("静かな情熱家", "慎重に見極めながら、新しい体験で愛を深める", ("観察力", "じっくり育てる情熱"), ("気持ちが伝わるまで時間がかかる",), "安心できる相手には、少しだけ自分から誘う回数を増やしてみよう。"),
 "1011": ("気ままな情熱家", "自分のペースを保ちつつ、恋の新鮮さを楽しむ", ("自分軸", "柔軟な発想"), ("相手には距離を置かれたと感じられることがある",), "一人の時間が必要な理由を伝え、次に会う予定も決めておこう。"),
 "1100": ("言葉のロマンチスト", "言葉で気持ちを伝え、安定した愛を育てる", ("表現力", "共感力"), ("言葉と行動の差が気になりやすい",), "約束を小さく具体的にして、言葉と行動の両方で信頼を育てよう。"),
 "1101": ("自由なロマンチスト", "言葉のつながりと個人の自由を両立する", ("感性豊かな対話", "独立した視点"), ("話し合いだけで満足してしまうことがある",), "話した内容を小さな行動に移すと、関係がより安定する。"),
 "1110": ("ときめきの開拓者", "行動と新鮮な体験で、恋に勢いを生み出す", ("決断力", "挑戦を楽しむ力"), ("勢いで進み、相手の不安を見落としやすい",), "新しいことを提案するときは、相手が安心できる選択肢も用意しよう。"),
 "1111": ("星追いの開拓者", "自由と新鮮さを大切にしながら、自分らしく恋をする", ("独創性", "自分らしさ"), ("関係を維持する連絡が少なくなりやすい",), "自由な関係ほど、二人で決めた約束を定期的に見直そう。"),
}
TYPES = {code: LoveType(code, *data) for code, data in _TYPES.items()}

@dataclass(frozen=True)
class LoveDiagnosis:
    code: str
    name: str
    tagline: str
    strengths: tuple[str, ...]
    blind_spots: tuple[str, ...]
    advice: str
    axis_results: tuple[tuple[str, str, int, int], ...]


def diagnose_answers(answers: dict[str, str]) -> LoveDiagnosis:
    missing = [q.id for q in QUESTIONS if answers.get(q.id) not in ("A", "B")]
    if missing:
        raise ValueError("恋愛タイプ診断の回答が不足しています：" + ", ".join(missing))
    bits = []
    axis_results = []
    for axis_index, (axis_name, a_label, b_label) in enumerate(AXES):
        qs = [q for q in QUESTIONS if q.axis == axis_index]
        a_count = sum(answers[q.id] == "A" for q in qs)
        b_count = len(qs) - a_count
        bit = "0" if a_count >= 2 else "1"
        bits.append(bit)
        axis_results.append((axis_name, a_label if bit == "0" else b_label, a_count, b_count))
    code = "".join(bits)
    t = TYPES[code]
    return LoveDiagnosis(code, t.name, t.tagline, t.strengths, t.blind_spots, t.advice, tuple(axis_results))


def self_test() -> str:
    assert len(QUESTIONS) == 12 and len(TYPES) == 16 and len(set(TYPES)) == 16
    # Every type code is reachable by choosing all A or B on each axis.
    for code in TYPES:
        answers = {}
        for q in QUESTIONS:
            answers[q.id] = "A" if code[q.axis] == "0" else "B"
        assert diagnose_answers(answers).code == code
    # Mixed answers and missing-answer rejection.
    answers = {q.id: "A" for q in QUESTIONS}
    assert diagnose_answers(answers).code == "0000"
    try:
        diagnose_answers({})
    except ValueError:
        pass
    else:
        raise AssertionError("missing answers were not rejected")
    return "OK: 12 questions; all 16 original types reachable; missing answers rejected."

if __name__ == "__main__":
    print(self_test())
