# 開発環境 — Draft 0.1

## v0.0選定の確定と導入手順

選定はbaseline-v0 §8、実際の確認値はenvironment-statusを参照する。
シミュレーションはUbuntu 24.04のiverilog 12.0-2build2とPython 3.12.3を基準とする。
未導入環境ではWSL2/Ubuntu 24.04をWindowsの公式手順で導入後、以下を実行する。
既存環境へ無断でインストール・更新することは今回の作業に含めない。

```sh
sudo apt-get update
sudo apt-get install iverilog gtkwave python3
iverilog -V
vvp -V
python3 --version
python3 docs/protocol-vectors.py
```

配布版が基準と異なる場合は差異を記録してテストを再実行する。
CIもUbuntu 24.04とし、実行時のツール版をログに保存する。
Gowin Educationはbaselineの1.9.9系を選定、公式配布元から対象デバイス対応版を取得する。
パッチ版、配布物ハッシュ、デバイス選択、ライセンス、書込みドライバーは実機準備Issueで固定する。
製品版とEducationを混在させず、導入できない場合は別フローを仕様変更としてレビューする。
プロジェクト作成から合成・配置配線・タイミング確認・書込みまでの順序はbaseline §8に従う。
実行できるtopと制約が揃った時点で#11に再現コマンドを記録する。

ピンの資料照合はenvironment-statusのコミット固定表を採用する。
pin4 reset_nとLED active-lowは実物・回路図照合のゲート項目であり、確認済みとはしない。
#6は選定と手順の策定、導入・物理照合は実機準備Issueに分離する。

> [実装基準仕様](baseline-v0.md)の§8と[環境確認記録](environment-status.md)を参照。候補の選定と実際の導入確認は区別する。

候補: Verilog、Icarus VerilogまたはVerilator、波形ビューア、GowinまたはOSS合成フロー、RISC-V GCC（-march=rv32i -mabi=ilp32）、Python PCローダー。いずれも採用・版は未確定で導入済みとはしない。

#6でWindows/WSLの選択、インストール元、バージョン固定、最小シミュレーション、合成・書込みコマンドを記録する。公式ボード回路図で実機版・UART配線・クロック・リセット極性を照合する。目標周波数とピン番号は未確定。

参照先（採用時に版を固定）: https://wiki.sipeed.com/hardware/en/tang/Tang-Nano-9K/Nano-9K.html / https://docs.riscv.org/reference/isa/ / https://github.com/riscv-non-isa/riscv-elf-psabi-doc
