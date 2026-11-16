# 開発計画 — Draft 0.1

期限は未設定。実装範囲は各段階のレビューで確定する。依存Issueが閉じるまで後続を開始しない。各マイルストーンは所属Issueの完了と以下の合格条件で閉じる。

## v0.0 仕様策定

完了条件: CPU・バス・メモリ・起動・検証の仕様をレビューし、実装を阻む未決事項を解消する。

- [#1 システム全体構成と対象範囲を決める](https://github.com/sutonomega/nanorv-32/issues/1)
- [#2 CPU命令・実行環境・停止動作を定義する](https://github.com/sutonomega/nanorv-32/issues/2)
- [#3 内部バスとRAM所有権の仕様を決める](https://github.com/sutonomega/nanorv-32/issues/3)
- [#4 メモリマップとMMIO副作用を定義する](https://github.com/sutonomega/nanorv-32/issues/4)
- [#5 UART転送・起動・復旧プロトコルを定義する](https://github.com/sutonomega/nanorv-32/issues/5)
- [#6 開発ツールとボード制約を選定する](https://github.com/sutonomega/nanorv-32/issues/6)
- [#7 命令検証と各段階の合格基準を策定する](https://github.com/sutonomega/nanorv-32/issues/7)

## v0.1 CPU基本動作

完了条件: 最小命令プログラムをシミュレーションで実行し、PC・レジスタ・RAMの期待値と一致する。

- [#8 ALU・レジスタ・デコーダーを実装する](https://github.com/sutonomega/nanorv-32/issues/8)
- [#9 マルチサイクルCPUと同期RAMを統合する](https://github.com/sutonomega/nanorv-32/issues/9)

## v0.2 RV32I対応

完了条件: 宣言した実行環境で全RV32I命令と異常系の検証結果を記録する。

- [#10 RV32I全命令と異常系を実装・検証する](https://github.com/sutonomega/nanorv-32/issues/10)

## v0.3 実機動作

完了条件: Tang Nano 9KでRAM初期化プログラムが動作し、資源・タイミング結果を保存する。

- [#11 Tang Nano 9Kへ合成・配置配線・書込みを行う](https://github.com/sutonomega/nanorv-32/issues/11)

## v0.4 PC連携

完了条件: UARTで転送・検証・実行・再起動を行い、破損データから復旧できる。

- [#12 UART・Boot Controller・PCローダーを実装する](https://github.com/sutonomega/nanorv-32/issues/12)

## v0.5 C言語対応

完了条件: 再現可能なビルドで生成したCプログラムが実機UARTにHello Worldを出力する。

- [#13 C実行環境とサンプルを整備する](https://github.com/sutonomega/nanorv-32/issues/13)

## v0.6 ミニOS

完了条件: モニターからプログラムをロード・実行し、終了後に操作へ戻れる。

- [#14 小型OSのABIと実行・復帰方式を設計する](https://github.com/sutonomega/nanorv-32/issues/14)
- [#15 モニターとプログラム管理を実装する](https://github.com/sutonomega/nanorv-32/issues/15)

## v1.0 ミニPC完成

完了条件: 新規環境から文書に従って構築し、転送・C実行・モニター操作の一連の検証に合格する。

- [#16 一連の実機検証とv1.0利用手順を完成させる](https://github.com/sutonomega/nanorv-32/issues/16)

## 運用

仕様変更は関連Issueと文書を同時更新し、判断理由と検証結果を残す。Issueは完了条件に証跡が揃ってから閉じる。実装変更はレビュー可能なPRを基本とする。初稿の登録は仕様承認ではない。保護機能・割り込み・外部メモリなど新たな必要作業は依存Issueとして追加する。
