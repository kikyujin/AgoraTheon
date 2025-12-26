# AgoraTheon 🏛️

AI討論会システム - 複数のLLM APIを使った討論シミュレーション

## 概要

**AgoraTheon**（アゴラテオン）は、Claude / Gemini / ChatGPT / Grok の4つのAI APIを使い、司会AI（スミレん）が進行する討論会システムです。

各AIが共有コンテキスト上で議論を積み上げ、ユーザーがリアルタイムで観戦・介入できます。

```
┌─────────────────────────────────────────┐
│ 【討論会】共有コンテキストウィンドウ      │
│                                         │
│  司会: 💠 スミレん（gemma3:27b）         │
│                                         │
│  参加者:                                │
│   ✴️ Claude   - 理性・深い推論           │
│   ❇️ Gemini   - 実用・高速               │
│   ♻️ ChatGPT  - 汎用・バランス           │
│   ♨️ Grok     - イーロン引用・ちゃぶ台返し │
│                                         │
│  観戦: マスター（介入可能）              │
└─────────────────────────────────────────┘
```

## インストール

```bash
# リポジトリをクローン or ZIPを展開
cd agoratheon

# 依存関係インストール
pip install -r requirements.txt
```

### 必要なAPI Key

以下の環境変数を設定してください：

```bash
export ANTHROPIC_API_KEY="sk-ant-..."    # Claude
export OPENAI_API_KEY="sk-..."           # ChatGPT
export GEMINI_API_KEY="..."              # Gemini
export GROK_API_KEY="xai-..."            # Grok
```

### スミレん司会（v1.1）の追加設定

デフォルトでOllama（gemma3:27b）を使用します：

```bash
# Ollamaを使う場合（デフォルト）
export SUMIRE_BACKEND=ollama
export OLLAMA_HOST=http://localhost:11434
export SUMIRE_MODEL=gemma3:27b

# Geminiを使う場合（Ollama無い環境向け）
export SUMIRE_BACKEND=gemini
```

## 使い方

### 基本起動

```bash
# 新規討論を開始
python agoratheon.py "AIの意識について.md"

# 既存の討論を再開（JSONから読み込み）
python agoratheon.py "AIの意識について.md"

# 参考資料付きで起動
python agoratheon.py "討論.md" --data 資料1.md --data 資料2.md

# 司会モードOFF（v1.0互換）
python agoratheon.py "討論.md" --no-auto

# APIヘルスチェック
python agoratheon.py --health
```

### 司会モード（v1.1）

テキストを入力するだけで、スミレんが最適なAIに振り分けます：

```
〉AIの倫理について議論したい
💠スミレん「Claudeさん、倫理的な観点からお願いします」

✴️claude: 倫理的には〜〜〜

〉（enter）
💠スミレん「Geminiさん、お願いします」

❇️gemini: 実用面では〜〜〜
```

### コマンド一覧

```
💠 司会モード:
  （テキスト入力）  - スミレんが最適なAIに振り分け
  （enter）        - 次のAIに順番に振る
  /auto           - 司会モード ON/OFF 切替

🎤 AI直接呼び出し:
  /claude [指示]   - ✴️ Claude（理性・深い推論）
  /gemini [指示]   - ❇️ Gemini（実用・高速）
  /chatgpt [指示]  - ♻️ ChatGPT（汎用・バランス）
  /grok [指示]     - ♨️ Grok（イーロン引用・ちゃぶ台返し）

🛠️ 編集:
  /filter          - 直前の発言をフィルタリング（NSFW対応）
  /delete          - 直前の発言を削除
  /summarize       - これまでの議論を要約

📊 その他:
  /status          - 現在の状態を表示
  /health          - APIヘルスチェック
  /save            - 討論を保存（JSON + Markdown）
  /bye             - 保存して終了
  /help            - ヘルプを表示
```

## ファイル構成

```
agoratheon/
├── agoratheon.py          # メインCLI
├── requirements.txt       # 依存関係
├── api/
│   ├── __init__.py
│   ├── claude.py          # ✴️ Anthropic API
│   ├── gemini.py          # ❇️ Google Gemini API
│   ├── chatgpt.py         # ♻️ OpenAI API
│   └── grok.py            # ♨️ xAI Grok API
├── models/
│   ├── __init__.py
│   └── discussion.py      # 討論データ構造
├── personas/
│   ├── __init__.py
│   └── sumire.py          # 💠 スミレん司会
└── utils/
    └── __init__.py
```

## 保存形式

討論は2つの形式で保存されます：

| ファイル | 用途 |
|----------|------|
| `討論.json` | 内部データ（自動保存、メタデータ完全保持） |
| `討論.md` | 人間用ビュー（`/save` 時に出力） |

- **自動保存**: 各操作後にJSONのみ自動保存（クラッシュ対策）
- **`/save`**: JSON + Markdown 両方を書き出し

## 各AIの特性

| AI | アイコン | 特性 | 得意分野 |
|----|----------|------|----------|
| Claude | ✴️ | 理性的・深い推論 | 倫理、哲学、論理的考察 |
| Gemini | ❇️ | 実用的・高速 | 最新情報、データ分析、具体案 |
| ChatGPT | ♻️ | バランス・汎用 | まとめ、多角的視点、一般質問 |
| Grok | ♨️ | ちゃぶ台返し | 斬新な視点、タブー、イーロン引用 |

## コスト目安

| 項目 | 費用 |
|------|------|
| 司会（Ollama） | 無料 |
| 各API（従量課金） | 数円〜数十円/発言 |
| **1回の討論会** | **10〜50円程度** |

## バージョン履歴

| バージョン | 機能 |
|-----------|------|
| v1.0 | 4API対応、手動コマンド、自動保存 |
| v1.1 | スミレん司会、自動振り分け |
| v1.2（予定） | コンテキストベース振り分け、NSFWオートフィルタ |

## 注意事項

- Grokの発言はNSFWになる場合があります。`/filter` で穏当な表現に書き換え可能です
- Geminiを司会に使う場合（`SUMIRE_BACKEND=gemini`）、NSFWな話題で振り分けが失敗する可能性があります
- 討論が長くなるとコンテキストが増え、API料金が上がります

## ライセンス

MIT License

## 作者

マスター & エルマー 🦊
