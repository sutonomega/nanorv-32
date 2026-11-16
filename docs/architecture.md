# 全体構成 — Draft 0.1

PC ↔ UART RX/TX ↔ Boot Controller / CPU用MMIO。CPUとBoot Controllerは所有権切替を介して同期RAMへ接続する。CPUはPC・Decoder・32bit ALU・レジスタファイル・FSMで構成する。

候補FSM: FETCH要求 → FETCH待機 → DECODE → EXECUTE → 必要に応じMEM要求/待機 → WRITEBACK。命令は一つずつ完了する。

候補バス: mem_addr[31:0], mem_wdata[31:0], mem_rdata[31:0], mem_wstrb[3:0], mem_valid, mem_ready。clkと同期rst、trap通知を持つ。valid && readyをクロック端で一度の完了とし、待機中は要求を保持する案。wstrb=0を読出しとする案。

転送中はCPU停止、実行中はCPUがRAMとUARTを所有する。CPUの停止と未完了アクセスの処理を確認して所有権を切り替える。リセットで必ずローダーへ復旧できる構成を目指す。

未確定: リセット解除同期、halt/開始PCの制御線、バスエラー線またはタイムアウト、同時完了と停止の優先順位、RAM初期化、UART FIFO深さ。#3 / #5 で時系列図を含め決定する。
