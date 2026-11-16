# NanoRV-32

[v0.0仕様策定の完了判定と残る実機ゲート](docs/specification-review.md)

Tang Nano 9K上の自作RV32I CPUと小型OSを段階的に育てるプロジェクト。現在は仕様策定中で、RTL・OSは未実装です。

## 仕様書（初稿）

- **[実装基準仕様 v0](docs/baseline-v0.md)** — PR #17で承認済み。下記初稿に優先する具体仕様。
- [開発環境・ボード制約の確認状況](docs/environment-status.md)
- [転送プロトコルの検証用ベクター生成](docs/protocol-vectors.py)

- [requirements](docs/requirements.md)
- [architecture](docs/architecture.md)
- [cpu-spec](docs/cpu-spec.md)
- [memory-map](docs/memory-map.md)
- [boot-protocol](docs/boot-protocol.md)
- [toolchain](docs/toolchain.md)
- [verification](docs/verification.md)
- [development-plan](docs/development-plan.md)

[Issue](https://github.com/sutonomega/nanorv-32/issues) / [マイルストーン](https://github.com/sutonomega/nanorv-32/milestones)

会話の設計案は承認済み仕様ではありません。各文書の候補値はv0.0でレビューします。過去案のv0.1の範囲には揺れがあったため、本リポジトリでは開発計画の8段階に統一します。参考: https://github.com/sutonomega/sound-canvas （日本語文書とIssueによる管理構成を参考にし、コードは流用していません）。ライセンスは未選定です。
