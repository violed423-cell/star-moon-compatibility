# Star & Moon / 星と月

独自12キャラクターと独自16恋愛タイプを組み合わせた、2人の相性を考えるためのエンターテインメント・自己理解用 Web アプリです。科学的な心理検査、相手の気持ちや未来の予測ではありません。

## 起動・再現

Python 3.12.14 で検証しました。

```sh
python -m venv .venv
# Linux / macOS
. .venv/bin/activate
# Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python public_app.py
```

http://127.0.0.1:8003 を開きます。pyswisseph のバイナリがない環境では C/C++ コンパイラが必要です。GCC 環境では `CC=gcc CXX=g++ LDSHARED='gcc -shared' pip install -r requirements.txt` で構築できます。

```sh
python test_public_app.py
python test_calendar_engine.py
python compatibility_v1_6.py
python love_type_16_v1_4.py
python test_星月自動相性診断_v1_6.py
python test_release_review.py
python test_source_offer.py
python -m compileall -q .
```

## 公開構成

Gunicorn: `gunicorn public_app:application --bind 0.0.0.0:$PORT --workers 2 --timeout 30`
Health: `/health`。Render 用の構成例は `render.yaml`。

コードの公開とサービス稼働は別です。規約、プライバシー、問い合わせ情報、ホスト側ログ・保存期間、レート制限、HTTPS、実機確認を完了するまで本番運用を開始しないでください。規約ページは未記入のテンプレートです。決済・DB・アカウント・診断履歴・メール機能はありません。`/premium` は将来の8～12ページ・暫定1,480円の商品案内のみです。

## 診断ルール

日本標準時。年は立春、月は節入り、日は午前0時に切り替えます。出生時刻不明の場合は正午で暫定判定し、境界日には注意を表示します。出生地・真太陽時・流派差は未対応です。暦の回帰テストは専門的照合の代わりではありません。

日干の五行で候補を限定し、月柱スコア、年柱スコア、固定順位の順で選びます。配分は木2・火3・土2・金3・水2。16タイプの質問・名称と0～100の相性スコアも独自の参考値です。

## 変更記録

v1.9 のソースを基に、日本語ファイル名の復元、月柱優先への訂正、JSTの今日判定、節入り日注意の表示、価格案の統一、追加回帰テスト、AGPLソース提供導線を追加しました。

## ライセンス・対応ソース

このプロジェクトの提供コードは GNU Affero General Public License v3.0（AGPL-3.0-only）で公開します。全文は `LICENSE`、依存関係の条件と出典は `THIRD_PARTY_NOTICES.md` を参照してください。明示・黙示の保証はありません。元の権利表示は維持し、第三者の権利をこの声明で変更しません。

利用者には各ページから `/source` を案内します。Render の `RENDER_GIT_COMMIT` が設定される本番では、そのコミットの対応ソースと ZIP へリンクします。他のホストで変更版を運用する場合は、その実際の対応ソースが取得できるようリンク先を更新し、AGPL条件を守ってください。個人情報や本番用秘密情報をソースに含めないでください。
