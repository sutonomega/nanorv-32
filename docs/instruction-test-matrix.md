# RV32I命令別検証計画

規範: RV32I v2.1、20240411公開版とbaseline-v0 §2/9。
全40行は未実施。#8〜#10でテスト名・コマンド・結果へのリンクを追記する。
各rd書込み命令はrd=x0とrs1/rs2/rd重複も検証する。
期待値はRTL制御信号を参照しない独立モデルで計算する。

| 命令 | 必須の指向性ケース | 状態 |
|---|---|---|
| LUI | 0/最大20bit、下位12bit=0 | 未実施 |
| AUIPC | 非ゼロPC、正負上位即値、32bit wrap | 未実施 |
| JAL | 前後方向、リンクPC+4、目標不整列、副作用なし | 未実施 |
| JALR | bit0クリア、負即値、rd=rs1、不整列 | 未実施 |
| BEQ | 等しい/異なる、前後方向、不成立の不整列先 | 未実施 |
| BNE | 等しい/異なる、前後方向、成立の不整列先 | 未実施 |
| BLT | signed最小/最大、等しい、成立/不成立 | 未実施 |
| BGE | signed負/正、等しい、成立/不成立 | 未実施 |
| BLTU | 0/FFFFFFFF、等しい、成立/不成立 | 未実施 |
| BGEU | 0/FFFFFFFF、等しい、成立/不成立 | 未実施 |
| LB | 各lane、7F/80/FFの符号拡張 | 未実施 |
| LH | lane0/2、7FFF/8000/FFFF、奇数違反 | 未実施 |
| LW | 00000000/FFFFFFFF、非整列違反 | 未実施 |
| LBU | 各lane、80/FFのゼロ拡張 | 未実施 |
| LHU | lane0/2、8000/FFFFのゼロ拡張、奇数違反 | 未実施 |
| SB | 各lane、隣接byte不変、下位8bitのみ | 未実施 |
| SH | lane0/2、隣接half不変、奇数違反 | 未実施 |
| SW | 全lane、書込み一回、非整列違反 | 未実施 |
| ADDI | 即値-2048/2047/-1、32bit wrap | 未実施 |
| SLTI | signed境界、負即値、等しい | 未実施 |
| SLTIU | 符号拡張即値をunsigned比較、0/FFFFFFFF | 未実施 |
| XORI | 即値0/-1、符号拡張、交互bit | 未実施 |
| ORI | 即値0/-1、符号拡張、交互bit | 未実施 |
| ANDI | 即値0/-1、符号拡張、交互bit | 未実施 |
| SLLI | shamt0/1/31、bit落ち、不正上位bit | 未実施 |
| SRLI | shamt0/1/31、ゼロ埋め、不正上位bit | 未実施 |
| SRAI | shamt0/1/31、負値の符号埋め、不正上位bit | 未実施 |
| ADD | 0/FFFFFFFF、符号境界、wrap | 未実施 |
| SUB | 同値、負結果、80000000-1、wrap | 未実施 |
| SLL | rs2=0/31/32/FFFFFFFF、下位5bit使用 | 未実施 |
| SLT | signed負/正、等しい、最小/最大 | 未実施 |
| SLTU | unsigned 0/FFFFFFFF、等しい | 未実施 |
| XOR | 同値/反転/交互bit | 未実施 |
| SRL | rs2=0/31/32/FFFFFFFF、ゼロ埋め | 未実施 |
| SRA | rs2=0/31/32/FFFFFFFF、符号埋め | 未実施 |
| OR | 0/全1/交互bit | 未実施 |
| AND | 0/全1/交互bit | 未実施 |
| FENCE | RAM/MMIOの先行完了後退役、後続順序保持、予約field無視 | 未実施 |
| ECALL | cause2、fault_pc、値0、停止後要求なし | 未実施 |
| EBREAK | cause3、fault_pc、値0、停止後要求なし | 未実施 |

全メモリ命令に未割当、MMIO幅/属性違反、RAM端境界、待機0/1/7cycleを追加する。
命令フェッチは未割当・MMIO・不整列を個別検証する。
illegalはM/C/CSR/FENCE.I、無効funct3/funct7を含む。
例外時の診断値と書込み抑止、resetと応答の同時性はbaseline-v0 §2〜4で判定する。

比較はretire時PC/命令語/rd値/メモリ副作用で行う。
例外で退役しない命令はtrapイベントとfault_pc/cause/valueを比較する。
バス副作用は受理端ごとに監視し、二重書込みや失敗アクセスの副作用を検出する。
テストが一つでも未実施なら#10を完了としない。
