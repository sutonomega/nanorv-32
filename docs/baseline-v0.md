# NanoRV-32 v0 実装基準仕様

状態: PR #17でレビュー・マージ済み。2026-11-16。環境の実確認状況は[確認記録](environment-status.md)を参照。
本書は初稿8文書の候補値に優先する。実装や実機適合を証明する文書ではない。
仕様変更はIssueと本書を同時に更新する。

## 1. 対象と設計判断

単一ハート、32bit、little endian、非パイプラインのマルチサイクルCPUを
Verilog-2005で自作する。初期は16 KiBの命令・データ共用同期RAM、UART、
6bit LED、32bitポーリングタイマーを備える。CPUの命令実装を先行し、
UARTローダー、C実行、協調型モニターへ進む。
割り込み、CSR、特権モード、MMU、メモリ保護、外部RAM、Flash保存、RV32M/C、
キャッシュ、パイプラインは初期範囲外。Linux対応は目標に含めない。

理由: 可変待機バスで拡張余地を保ち、初期の回路規模と検証対象を小さくする。
OSは信頼できる単一アプリを呼び出すモニターとし、プリエンプションや
不正アプリからの保護を保証しない。

資源目標はLUT4 6,000以下、内蔵RAM使用量24 KiB以下。
これらは設計予算であり合成結果ではない。超過時は仕様変更をレビューする。
クロックは27 MHz単一ドメイン、PLLなしを目標とする。
27 MHzでタイミングを満たさない場合、無断で制約を緩めず計画を見直す。

## 2. CPUと実行環境

XLEN=32、x0〜x31、IALIGN=32。x0書込みは捨てる。
リセット時の全レジスタは0、PC=0。PC通常更新は+4。
命令はFETCH_REQ → FETCH_WAIT → DECODE → EXECUTE →
必要ならMEM_REQ/MEM_WAIT → WRITEBACKで一つずつ完了する。
同期RAMの読出しに必ず待機状態を設ける。

対象はRV32I v2.1（20240411公開版）と本書の実行環境。
命令ビット配置・即値・算術意味は下記公式仕様を規範とする。

| 群 | 全対象命令 |
|---|---|
| 上位即値 | LUI AUIPC |
| ジャンプ | JAL JALR |
| 分岐 | BEQ BNE BLT BGE BLTU BGEU |
| 読出し | LB LH LW LBU LHU |
| 書込み | SB SH SW |
| 即値演算 | ADDI SLTI SLTIU XORI ORI ANDI SLLI SRLI SRAI |
| レジスタ演算 | ADD SUB SLL SLT SLTU XOR SRL SRA OR AND |
| 順序・環境 | FENCE ECALL EBREAK |

シフト量は下位5bit。加減算は下位32bit、算術オーバーフロー例外なし。
JALRは加算後bit0をクリアし、その後4byte境界を確認する。
不整列ジャンプはリンクレジスタを書かず、原因となった命令で停止する。
分岐先不整列は分岐成立時のみ検出する。
LB/LHは符号拡張、LBU/LHUはゼロ拡張する。
x0宛ロードも実アクセス・副作用・エラー検出を行う。
FENCEは先行アクセス完了後に退役し、後続アクセスをそれ以前に発行しない。
単一要求・順序実行のため追加回路不要。FENCEの予約フィールドは公式規定に従う。
FENCE.I、CSR、M/C命令および不正エンコードはillegal停止。
標準HINTは副作用のない通常の定義に従い退役する。

ECALL/EBREAKは致命的環境トラップとして停止する。Machineモード準拠は宣言しない。
不整列ロード/ストアは分割しない。例外検出時に要求を発行せず副作用を生じさせない。
原因番号は本プロジェクトの診断番号でありmcauseではない。

| 番号 | 原因 | fault_value |
|---|---|---|
| 1 | illegal instruction | 命令語 |
| 2 | ECALL | 0 |
| 3 | EBREAK | 0 |
| 4 | 命令アドレス不整列 | 対象アドレス |
| 5 | 命令アクセス違反 | 対象アドレス |
| 6 | データアドレス不整列 | 対象アドレス |
| 7 | ロードアクセス違反 | 対象アドレス |
| 8 | ストアアクセス違反 | 対象アドレス |

同一命令では不正デコード、不整列、アクセス違反の順に判定する。
trap、fault_pc、fault_cause、fault_valueを保持し、リセットまで復帰しない。
停止後はバス要求を出さず、外部リセットでのみローダーへ戻る。
シミュレーションでは全診断値を観測可能にする。
実機ではtrap時にLEDへ原因の下位6bitを表示する。詳細レジスタ読出しは後続課題。

## 3. バス契約

clk、同期active-high rstに加え、要求はvalid、addr[31:0]、wdata[31:0]、
wstrb[3:0]、size[1:0]、instr。応答はready、rdata[31:0]、error。
size=0/1/2は1/2/4byte、3は禁止。instr=1は命令フェッチ。
wstrb=0は読出し。書込みデータはアドレス下位2bitに従いlaneへ配置する。
読出し応答は整列した32bitワードを返し、CPUが抽出・拡張する。
sizeを加える理由はMMIOの不正なバイト/ハーフワード読出しを識別するため。

valid && readyを立上りで一度受理し、その端でのみ副作用を確定する。
ready=0中は全要求信号を保持する。要求は常に一件のみ。
完了の次サイクルは必ずvalid=0とし、同じ要求の再受理を防ぐ。
errorはreadyと同時のみ有効。エラー書込み・読出しには副作用がない。
未割当・幅違反・権限違反は有限時間でerrorを返す。
キャッシュも投機実行もない。フェッチはRAM内の4byte読出しのみ許す。

例（各行は立上り直前の値）:

| 端 | valid | ready | 動作 |
|---|---|---|---|
| N | 1 | 0 | 要求保持 |
| N+1 | 1 | 1 | 応答取得・副作用一度 |
| N+2 | 0 | 0 | 要求なし |
| N+3 | 1 | 0 | 次要求 |

RAMは同期読出しとバイト書込み、初期内容は未定義。
ローダーが有効と認めたイメージ以外は実行しない。
シミュレーション用イメージ初期化はローダーを使わない検証モードとして明示する。

## 4. リセット・所有権

外部リセットは非同期アサート・2段同期解除するリセット回路を経由し、
各機能モジュールへ同期rstを配る。UART RXは2段同期化する。
ボタン入力はリセット用途のみで、解除のチャタリングでも安全にCPU停止へ戻る。

BOOT状態ではCPUをreset保持し、Boot ControllerがRAM/UARTを所有する。
検証成功後、STARTのACK送信完了を待ち、1cycleの無要求状態を経てRUNへ遷移する。
RUNではCPUだけがRAM/UARTを所有する。ローダーはフレームを解釈しない。
trap時はCPUを停止したままにし、自動でRAM所有権を渡さない。
実行中のUART制御文字による停止は提供しない。
リセットは全状態より優先し、未完了要求を破棄、validとFIFOをクリアする。
リセット端でのRAM書込みは抑止する。RAM全域はクリアしないがimage_valid=0とする。

## 5. メモリとMMIO

RAM 0x00000000〜0x00003FFFはR/W/X。全幅アクセス可、自然境界必須。
MMIOは4byte整列LW/SWのみ、命令フェッチ不可。下記以外はアクセス違反。

| アドレス | 属性 | リセット | 定義 |
|---|---|---|---|
| 0x10000000 | W | — | UART TX、下位8bit送信 |
| 0x10000004 | R | 0 | UART RX、下位8bit。受理時にpop |
| 0x10000008 | R | 2 | bit0 RX有、bit1 TX空き有、bit2 overrun、bit3 framing error |
| 0x1000000C | W | — | bit2/3に1を書いて対応エラーをclear |
| 0x10000100 | R/W | 0 | LED下位6bit、1=点灯という論理表現 |
| 0x10000200 | R | 0 | 32bit 1μs tick、2^32でwrap |
| 0x10000204 | R/W | 0 | bit0 enable、bit1 write-oneでcounter/divider clear |

RO書込み/WO読出しはerror。予約bit読出しは0、書込みは無視。
TX満杯書込みとRX空読出しは即時errorとし、無期限のCPU待機を作らない。
ソフトはSTATUSを確認する。RX/TX FIFO各16byte、同時push/popを許す。
RX満杯時は到着した新byteを捨てoverrunを立てる。
フレーミング不正byteは捨てframing errorを立てる。clearと新エラー同時ならset優先。
タイマーは27cycle分周、停止中はcounter/divider保持。clearがenable更新より計数上優先。
CONTROL読出しはbit0のみ返す。割り込みなし。
LEDはtrap時のみ診断表示が通常値に優先する。

## 6. UARTローダープロトコル v1

115200 baud、8 data、no parity、1 stop、flow controlなし。
27 MHzから整数分周234cycle/bitを使用する。
RXはstart中央確認後、各bit中央で採取し、stop=1を確認する。
PCは一フレーム送信後応答を待つ。応答待ち上限2秒、失敗時はリセットして全転送をやり直す。

フレームは magic[4] + version[1] + command[1] + length[4] + payload[length] + crc[4]。
magic=4E 52 56 31（NRV1）、version=01。多byte整数はlittle endian。
CRCはversionからpayload末尾までを対象としmagicを含まない。
CRC-32/ISO-HDLC: poly=04C11DB7、reflected実装poly=EDB88320、
init=FFFFFFFF、refin/refout=true、xorout=FFFFFFFF。
標準チェック文字列123456789の結果はCBF43926、wire上は26 39 F4 CB。

| command | payload | 動作 |
|---|---|---|
| 01 LOAD | 4〜16384byte、4の倍数 | RAM 0から格納、成功時image_valid=1 |
| 02 START | 空 | image_valid時のみPC=0で起動 |
| 81 ACK | 元command[1], status=00[1] | 成功応答 |
| 82 NACK | 元command[1], status[1] | 失敗応答 |

LOAD開始時にimage_validを落とし、CRC成功でのみ上げる。
転送末尾以降のRAM内容は不定。送信イメージには必要なコード・data・パディングを含める。
CRC不一致でも一部RAMは変更され得るがSTARTは拒否する。
STARTではACKのstop bit送信完了後にUART FIFOをクリアしてRUNへ切り替える。
CPUのレジスタはreset値0から開始する。
NACK status: 01 version、02 command、03 length、04 CRC、05 imageなし、06 timeout。
エラー優先はversion → command → length → CRC → image状態。
フレーム途中の受信間隔100ms超でtimeoutとしimage_valid=0、
分かっているcommandを付けNACK（不明なら00）を返して同期探索へ戻る。
長さ不正時は受信を中止しNACK後に同期探索する。
エラー後はPCが送信を止め、リセットして再送することを必須とする。
UART受信エラーも転送無効化し同期探索へ戻す。成功した既存イメージも再転送が必要。
フレーム例・CRC付き全byte列は検証用ベクターを参照する。

## 7. CとOSへの接続

GCCは-march=rv32i -mabi=ilp32 -ffreestanding -mno-relax、
リンクは-nostdlib -Wl,--no-relaxを基本とする。必要なlibgcc補助関数は
rv32i/ilp32のもののみを明示リンクする。
startupはsp=0x4000、gp設定、data初期化、bssゼロ化、main呼出しを行う。
ベアメタルmain復帰はEBREAK停止。ヒープは初期には提供しない。
スタック1 KiBを最低予約し、リンク時に配置衝突を拒否する。

v0.6ではRAM下位8 KiBをモニター、0x2000〜0x3BFFをアプリ、
0x3C00〜0x3FFFを共有スタックとする案を#14で容量測定後に確定する。
アプリは通常関数として呼び出し、ABIに従いcallee-savedレジスタを保存して戻る。
ECALLによるsyscallは初期には設けない。メモリ保護はない。
アプリ異常・無限ループの復旧はハードリセットと再ロード。
アプリ復帰ABIの詳細はv0.6の設計でありCPU実装の前提としない。

## 8. 開発環境と実機ゲート

シミュレーションはWSL2 Ubuntu 24.04、Icarus Verilog 12.0、
GTKWave 3.3系、Python 3.12標準ライブラリを基準とする。
合成・配置配線はWindows版Gowin EDA Education 1.9.9系を選定する。
CコンパイラはGCC 14系のriscv-none-elfまたはriscv64-unknown-elfを使用し、
rv32i/ilp32 multilibの存在を採用条件とする。
導入は各公式配布元を使用し、実装時にパッチ版・取得元・ハッシュを環境記録へ固定する。
本仕様段階ではインストール・ライセンス適合・動作確認を実施していない。

想定ボードはTang Nano 9K、GW1NR-LV9QN88PC6/I5。
公式ボード資料とサンプル制約を基準に、実装担当は手元の基板版・部品刻印・
クロック/UART/LED/リセットの接続と極性を確認する。
未照合のピンを推測で制約ファイルへ書かない。
実機書込みは#6の接続照合と#11の制約レビューが完了するまで禁止する。

導入確認: iverilog -V、vvp -V、python3 --version、
riscv64-unknown-elf-gcc --version、同 -print-multi-lib。
将来の検証コマンド契約（ファイルは#8以降に追加、現時点では実行不可）:
iverilog -g2005 -s tb_alu -o build/tb_alu sim/tb_alu.v rtl/cpu/alu.v、
vvp build/tb_alu。CPU/SoCも同様にテストトップと必要ソースを明示列挙する。
合成は選定EDAでtop、対象型番、27 MHz制約、照合済みCSTを登録し、
Synthesis → Place and Route → Timing Report → Programmerの順に実施する。
再現スクリプトと正確な版固定は#6の残作業とする。

## 9. 検証契約

単体はALU全演算、即値形式、x0、同一レジスタ読書き、不正デコードを検証する。
各命令は正常・境界値・宛先x0を、分岐はtaken/not-takenを含める。
ロード/ストアは各幅・各lane・符号境界・不整列・未割当を網羅する。
JAL/JALRはリンク値・bit0クリア・不整列を含める。
FENCE順序、ECALL/EBREAK診断、失敗命令の副作用なしを確認する。
バス待機は0/1/7cycle、所有権切替、応答とリセット同時、
FIFO空/満杯/同時push-pop、タイマーwrap/clearを検証する。
ローダーは正常・CRC不正・長さ不正・切断・受信異常・START拒否・再転送を確認する。

命令退役時のPC、命令語、rd書込み、メモリ副作用をトレース出力する。
Pythonの独立した命令意味モデルと照合し、RTL内部制御をモデルへ流用しない。
固定seedによるランダム命令試験を補助に用いるが、全命令の指向性試験を必須とする。
既存適合テスト導入は補助課題とし、全特権適合の証明とは扱わない。

単体/CPUは1ケース100000cycle、ローダーは100000000cycleを上限とし、
超過はFAIL。成功はPASSと件数、失敗は入力・期待・実際値を出力して非ゼロ終了。
CIはGitHub Actions Ubuntu上でシミュレーションとプロトコルベクターを実行する。
Gowin合成と実機確認は別の手動ゲートとし、CI成功だけで実機合格としない。
版・コミット・コマンド・seed・ログ・資源・タイミング結果を検証記録へ保存する。
全40命令と異常系のチェック表が埋まるまでRV32I実装完了を宣言しない。

## 10. 未確定事項と閉じ方

CPU/バス/MMIO/転送契約は本書で選定した。実装に必要な変更はIssueで追跡する。
手元のボード照合、EDAパッチ版・導入確認は実機準備Issueに残す。
top作成後の合成再現スクリプトは#11で検証する。
OS容量・ABI詳細は#14、公開ライセンス選択は別Issueとする。
これらを実施済みとは扱わない。#6はツール・ボード制約の選定を担当し、
実機の照合・EDA導入と合成実行は独立した実機準備Issueを#11の必須依存にする。
仕様策定と実機試験を分けるための計画変更であり、確認条件を削除するものではない。
v0.0は#6の選定記録と#7の検証計画のレビュー・マージ後に完了できる。

## 公式参照

- https://docs.riscv.org/reference/isa/v20240411/unpriv/rv32.html
- https://en.wiki.sipeed.com/hardware/en/tang/Tang-Nano-9K/Nano-9K.html
- https://github.com/sipeed/TangNano-9K-example
- https://github.com/riscv-non-isa/riscv-elf-psabi-doc
- https://steveicarus.github.io/iverilog/
- https://www.gowinsemi.com/en/support/download_eda/
