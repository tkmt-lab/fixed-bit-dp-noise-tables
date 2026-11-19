# 固定ビットの差分プライバシー表とサンプラー

**v1.0.0 · 公開日: 2026-11-19 · DOI: 未付与** · [Repository](https://github.com/tkmt-lab/fixed-bit-dp-noise-tables) · [English](README.md)

最大12個の公平な乱数ビットで使う有限整数確率表とサンプラーを生成します。
固定ビットの機構を試す研究者・開発者が、指定した隣接関係の純粋な差分プライバシーと、最適性・実行不能の厳密な証明記録を検査できます。

## 最初の例

この一式のルートで実行。Python 3.11+、NumPy、highspy、clang が必要です（macOS/Linux）。

```sh
python3 -B cli.py examples/counting.json --out ../dp-output
python3 -B checker.py ../dp-output/result.json
python3 -B checker.py ../dp-output/result.json --proof-only
```

期待結果: `OPTIMAL`、`loss: "7/12"`、検査は `PASS`。

出力先は `../dp-output/`、ファイルは `result.json`、`sampler.py`、`sampler.c` と C サンプラーの検査用共有ライブラリ（Linux は `sampler.so`、macOS は `sampler.dylib`）です。

## 模型・入力・出力

入力状態ごとの表は非負整数で、行和は 2^b です。有理数のプライバシー倍率 r と指定した隣接辺について、両方向の整数不等式を検査します。禁止セルと度数の上下限も指定できます。非負有理数の損失行列を使い、入力の一様分布で期待損失を最小化します。固定ベンチマークは完全隣接、r=2、k=3..8、b=4..12 と合成の巡回非対称損失です。

JSON の項目は `D`、`Y`、`edges`、`r`、`b`、`loss`、任意の `output_constraints` です。[examples/](examples/) を参照してください。ラベルは入出力を識別し、辺とサンプラーの引数には配列の添字を使います。生成器は `result.json` と、表があれば Python/C サンプラーを書きます。厳密な証明記録を検査できた場合だけ `OPTIMAL` または `UNSAT` とし、それ以外の検査済み表は `FEASIBLE`、表を得られず探索が未解決なら `UNKNOWN` です。不正な仕様はエラーとします。

生成には Python 3.11+、NumPy、HiGHS の Python binding `highspy` と clang が必要です。依存するソフトウェアは、それぞれのライセンスに従って別途導入してください。

## 保存済み結果を検査する

同じ一式のルートで次を実行します。こちらは Python 標準ライブラリと clang だけで動きます。

```sh
python3 -B verify.py
```

期待結果は `status: "PASS"`、証明記録60件（OPTIMAL 56、FEASIBLE 3、UNSAT 1）、過去の Python/C 108組、1,079,232写像呼出しです。通常検査と別実装の仕様→制約検査を使い、偽造UNSAT証明を拒否し、全乱数語を列挙します。改良例と追加例のサンプラーも別途検査します。一時ビルドは一時ディレクトリへ出します。

C の共有ライブラリは macOS で `-dynamiclib` / `.dylib`、Linux で `-shared -fPIC` / `.so` を使い、`-Werror` を維持します。検査時は Python の assert を有効にしてください。

## 保存済みの結果

54条件の過去の直接生成表のうち、51件には独立実装で確認した最適性証明があります。k=5,b=11 の旧表は実行可能で、整数費用は16093です。同梱した改良表の費用は16092で最適性証明があります。これを数えると54条件中52条件に最適性証明があります。k=7,b=5 と k=7,b=9 は実行可能で、最適性は未確定です。追加の例4件の最適性と1件の実行不能証明も検査しています。過去のサンプラー108組のラベルは FEASIBLE とし、旧solverの数値ラベルを履歴の項目として保持しています。

証明は有理数双対境界と完全な整数分枝木を使います。主生成器と主検査器は標準形の構築を共有し、別実装の検査器は仕様から制約を再構成します。方法は [PROOF.md](PROOF.md)、主張と根拠の対応は [claims.json](claims.json) を参照してください。

## 範囲

保証の対象は、同梱した有限の仕様と証明記録です。新しい一般定理や一般的な新規性を示すものではなく、合成ベンチマークはすべてのプライバシー用途を模型化するものではありません。検証は研究室内の別実装と通常の Python の有理数検査によるもので、人による査読や検査器の形式証明ではありません。履歴に残したsolverの数値ラベルは証明書ではありません。

呼出側は有効な入力添字と独立一様な b-bit 乱数語を渡す必要があります。C/Python サンプラーは有効な引数に対して1回の表参照を行いますが、参照アドレスは入力に依存します。定数時間、サイドチャネル耐性、安全な乱数源、暗号学的安全性、実機性能は保証していません。各用途で模型と実装の適合性を評価してください。

この配布版には Rust `lut_sampler` で新たに生成した表との比較は含めず、近似サンプリング道具の欠陥は主張しません。再実行の環境・結果とビルドの経緯は [VERIFICATION-RECORD.md](VERIFICATION-RECORD.md) にまとめています。C サンプラーの検査は macOS と Linux に対応し、他の OS は対象外です。謝辞は利用した仕事への感謝であり、各著者による本成果の支持を意味しません。

## AI の利用と責任

OpenAI Codex が文献を調べ、表の生成器とサンプラーを実装し、ベンチマークの計算と説明文の下書きを行いました。
Codex に指定したモデルには `gpt-6.1-sol`、`gpt-6.1-terra`、`gpt-6-astra` があります。個々の実行でどの版が使われたかまでは、記録から特定できません。
別の Codex エージェントが検算用のコードを書き、サンプラーの出力を表と照合し、仕様から制約を組み立て直して有理数の証明書を検査しました。
この検算は AI エージェントによるもので、人による査読ではありません。

Anthropic Claude Opus 5.5 は、macOS 専用のコンパイル指定が原因で Linux での検査が止まった経緯の記録を助けました。
Google Gemini は、分布の近似と純粋な差分プライバシーの違いを説明する文案を作りました（Gemini 4 の環境。実行時の詳しい版は記録なし）。
この一式のコード、データ、主張には著者の滝本竜彦が責任を負います。

## 謝辞・連絡先

Peter Kairouz、Keith Bonawitz、Daniel Ramage の局所プライバシー下の離散分布推定研究を、標準的な k-ary randomized-response の基準として参照しました。この研究の著者、最適化ソフトウェアを提供した HiGHS 開発者、分布近似の公開実装 Optimal Approximate Sampling を提供した Feras A. Saad、Cameron E. Freer、Martin C. Rinard、Vikash K. Mansinghka、`lut_sampler` と公表された近似表を提供した Fabian Schmid に謝意を表します。出典は [SOURCES.md](SOURCES.md) にあります。

著者は滝本竜彦（Tatsuhiko Takimoto）。研究用の連絡先は [research@tatsuhikotakimoto.com](mailto:research@tatsuhikotakimoto.com) です。

プロジェクトのコードは Apache-2.0、独自のデータ・文書は CC-BY-4.0 です。[LICENSE](LICENSE) を参照してください。他者のソフトウェア・論文は各出典から、それぞれのライセンスに従って取得してください。

## 版の履歴と文書の写し

[CHANGELOG.md](CHANGELOG.md) に版の履歴があります。

[PACKAGE.pdf](PACKAGE.pdf) は英語 README・証明方法・検証記録・出典・変更履歴、[README.ja.pdf](README.ja.pdf) はこの日本語文書です。`MANIFEST.sha256` は自身以外の全ファイル（PDFを含む）を固定します。再生成には Pandoc・XeLaTeX・xeCJK・DejaVu・Noto CJK フォントを導入し、`python3 -B build_docs.py` を実行してください。[build_docs.py](build_docs.py) 内の命令で全ファイルの目録を作り直し、`python3 -B verify.py` を実行します。これらの追加の道具は PDF の生成だけに使います。
