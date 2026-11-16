# 開発環境・ボード制約の確認記録

2026-11-16。PR #17はレビュー・マージ済み。本書はその後の確認記録。

## 確認済み

WindowsからWSL Ubuntu-24.04を起動できる。
WSL内のiverilogとvvpはともに12.0 stable、Pythonは3.12.3。
WindowsのPythonは3.12系。WSL内のriscv64-unknown-elf-gccはPATHに存在しない。
Gowinのインストール状況、ライセンスと対象デバイスの利用可否は未確認。
この記録はツールのバージョン取得までで、合成・書込み合格を意味しない。

再確認コマンド（Windows PowerShell）:

```powershell
wsl -d Ubuntu-24.04 -- iverilog -V
wsl -d Ubuntu-24.04 -- vvp -V
wsl -d Ubuntu-24.04 -- python3 --version
wsl -d Ubuntu-24.04 -- sh -lc 'command -v riscv64-unknown-elf-gcc'
```

## 公式サンプルによる配線照合

参照コミット: c3b795799f23de91982be52db4273a8eea100cdb。
https://github.com/sipeed/TangNano-9K-example/tree/c3b795799f23de91982be52db4273a8eea100cdb

| 信号 | ピン | 参照 |
|---|---|---|
| clk | 52 | uart/src/top.cst と led/src/9K_LED_project.cst |
| FPGA UART TX | 17 | uart/src/top.cst |
| FPGA UART RX | 18 | uart/src/top.cst |
| LED[0..5] | 10,11,13,14,15,16 | led/src/9K_LED_project.cst |
| 外部reset_n | 4を採用予定 | LED例のsys_rst_n。UART例はrst_n=3 |

UART例にはGW1NR-LV9QN88PC6/I5と記載される。
リセットピンは両例で異なるため、同一信号とみなして混在させない。
本プロジェクトはLED例のボタン系統（pin4）を採用予定とする。
手元の基板の刻印と公式回路図でpin4のボタン接続・active-lowを確認してから確定する。
LEDの物理極性も同様に確認する。仕様上の1=点灯はtopで物理極性へ変換する。
未確認のままCSTを生成・書込みしない。

## 残っている確認と担当境界

- 手元の基板版・FPGA刻印・ボタン/LED極性: 実物を持つ担当者が確認。
- Gowinの正確な版・インストール先・Educationでの対象デバイス選択: 実機準備時に確認。
- Cツールチェーンの導入とrv32i/ilp32 multilib確認: #13の前に実施。
- 合成・配置配線の自動化と正確な実行手順: top/CST作成後の#11で検証。

#6は実物確認とEDA導入確認が残るため未完了。
仕様策定段階で実装未存在の合成手順を実行済みとは扱わない。
