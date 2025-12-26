#!/usr/bin/env python3
"""
AgoraTheon - AI討論会システム
v1.0: 直接指定コマンド版
"""

import sys
import os
import argparse
import readline  # 入力履歴用

# パスを通す
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import API_MAP, ICONS
from models import Discussion


class AgoraTheon:
    """AI討論会メインクラス"""
    
    def __init__(self, discussion_file: str, data_files: list = None):
        self.discussion_file = discussion_file
        self.discussion = self._load_or_create(discussion_file)
        
        if data_files:
            self.discussion.data_files.extend(data_files)
        
        # APIインスタンス（遅延初期化）
        self._apis = {}
    
    def _load_or_create(self, filepath: str) -> Discussion:
        """討論ファイルを読み込むか新規作成（JSONのみ対応）"""
        title = os.path.splitext(os.path.basename(filepath))[0]
        json_file = filepath.replace('.md', '.json')
        
        # JSONファイルがあれば読み込み
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                return Discussion.from_json(f.read())
        
        return Discussion(title=title)
    
    def _get_api(self, name: str):
        """APIインスタンスを取得（遅延初期化）"""
        if name not in self._apis:
            if name not in API_MAP:
                raise ValueError(f"Unknown API: {name}")
            self._apis[name] = API_MAP[name]()
        return self._apis[name]
    
    def _get_context(self) -> str:
        """討論コンテキストを取得"""
        context = self.discussion.get_context()
        
        # 参考資料があれば追加
        data_context = []
        for filepath in self.discussion.data_files:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data_context.append(f"【資料: {filepath}】\n{f.read()}")
        
        if data_context:
            return "\n\n".join(data_context) + "\n\n" + context
        return context
    
    def _auto_save(self):
        """JSONのみ自動保存"""
        json_file = self.discussion_file.replace('.md', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(self.discussion.to_json())
    
    def call_api(self, api_name: str, prompt: str = "") -> str:
        """指定したAPIを呼び出して発言を追加"""
        api = self._get_api(api_name)
        context = self._get_context()
        
        response = api.generate(context, prompt)
        
        # 発言を追加
        self.discussion.add_message(api.NAME, api.ICON, response)
        
        # 自動保存
        self._auto_save()
        
        return f"{api.ICON}{api.NAME}: {response}"
    
    def cmd_filter(self) -> str:
        """直前の発言をフィルタリング"""
        last = self.discussion.get_last_message()
        if not last:
            return "フィルタ対象の発言がありません"
        
        # Grok（キャラ無し）でフィルタリング
        filter_prompt = f"""以下の発言から不適切な表現（性的、暴力的、差別的など）を除去し、
穏当な表現に書き換えてください。
元の意味はできるだけ保持してください。

【元の発言】
{last.content}

【書き換え後の発言のみを出力】"""
        
        try:
            from openai import OpenAI
            import os
            client = OpenAI(
                api_key=os.environ.get('GROK_API_KEY'),
                base_url="https://api.x.ai/v1"
            )
            response = client.chat.completions.create(
                model="grok-3-fast",
                messages=[{"role": "user", "content": filter_prompt}],
                temperature=0.3,
                max_tokens=2048
            )
            filtered = response.choices[0].message.content.strip()
        except Exception as e:
            return f"フィルタエラー: {e}"
        
        self.discussion.filter_last(filtered)
        self._auto_save()
        return f"*{last.icon}{last.speaker}: {filtered}"
    
    def cmd_delete(self) -> str:
        """直前の発言を削除"""
        if self.discussion.delete_last():
            self._auto_save()
            return "直前の発言を削除しました"
        return "削除対象の発言がありません"
    
    def cmd_summarize(self) -> str:
        """これまでの議論を要約"""
        context = self.discussion.get_context()
        if not context:
            return "要約する議論がありません"
        
        # Geminiで要約
        api = self._get_api("gemini")
        
        summary_prompt = f"""以下の討論を簡潔に要約してください。
各参加者の主要な主張と、議論の流れをまとめてください。

【討論内容】
{context}

【要約】"""
        
        try:
            from google import genai
            from google.genai import types
            import os
            client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=summary_prompt,
                config=types.GenerateContentConfig(max_output_tokens=2048)
            )
            summary = response.text.strip()
        except Exception as e:
            return f"要約エラー: {e}"
        
        # 要約を司会として追加
        self.discussion.add_message("sumire", ICONS["sumire"], f"【これまでの議論要約】\n{summary}")
        
        self._auto_save()
        return f"{ICONS['sumire']}sumire: 【これまでの議論要約】\n{summary}"
    
    def cmd_save(self) -> str:
        """討論を保存"""
        # JSON形式で内部保存
        json_file = self.discussion_file.replace('.md', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(self.discussion.to_json())
        
        # Markdown形式でも保存
        with open(self.discussion_file, 'w', encoding='utf-8') as f:
            f.write(self.discussion.to_markdown())
        
        return f"保存しました: {self.discussion_file}, {json_file}"
    
    def cmd_status(self) -> str:
        """現在の状態を表示"""
        lines = [
            f"📋 タイトル: {self.discussion.title}",
            f"💬 発言数: {len([m for m in self.discussion.messages if not m.deleted])}",
            f"📁 参考資料: {len(self.discussion.data_files)}件",
        ]
        return "\n".join(lines)
    
    def cmd_health(self) -> str:
        """APIヘルスチェック"""
        results = []
        for name in API_MAP.keys():
            try:
                api = self._get_api(name)
                status = api.health_check()
                icon = "✅" if status["status"] == "healthy" else "❌"
                results.append(f"{icon} {ICONS[name]}{name}: {status['status']}")
            except Exception as e:
                results.append(f"❌ {ICONS[name]}{name}: {e}")
        return "\n".join(results)
    
    def process_command(self, line: str) -> tuple[str, bool]:
        """
        コマンドを処理
        
        Returns:
            (出力文字列, 終了フラグ)
        """
        line = line.strip()
        
        if not line:
            return "", False
        
        # /コマンド処理
        if line.startswith('/'):
            parts = line[1:].split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            
            # API呼び出し
            if cmd in API_MAP:
                return self.call_api(cmd, arg), False
            
            # 特殊コマンド
            if cmd == "filter":
                return self.cmd_filter(), False
            elif cmd == "delete":
                return self.cmd_delete(), False
            elif cmd == "summarize":
                return self.cmd_summarize(), False
            elif cmd == "save":
                return self.cmd_save(), False
            elif cmd == "status":
                return self.cmd_status(), False
            elif cmd == "health":
                return self.cmd_health(), False
            elif cmd == "bye":
                self.cmd_save()
                return "討論を終了します。お疲れ様でした！", True
            elif cmd == "help":
                return self._help(), False
            else:
                return f"不明なコマンド: /{cmd}\n/help でヘルプを表示", False
        
        # コマンドなしの入力（v1.0では無視）
        return "コマンドを入力してください（/help でヘルプ表示）", False
    
    def _help(self) -> str:
        """ヘルプ表示"""
        return """【AgoraTheon v1.0 コマンド一覧】

🎤 AI呼び出し:
  /claude [指示]   - ✴️ Claude（理性・深い推論）
  /gemini [指示]   - ❇️ Gemini（実用・高速）
  /chatgpt [指示]  - ♻️ ChatGPT（汎用・バランス）
  /grok [指示]     - ♨️ Grok（叡智・ちゃぶ台返し）

🛠️ 編集:
  /filter     - 直前の発言をフィルタリング
  /delete     - 直前の発言を削除
  /summarize  - これまでの議論を要約

📊 その他:
  /status     - 現在の状態を表示
  /health     - APIヘルスチェック
  /save       - 討論を保存
  /bye        - 保存して終了
  /help       - このヘルプを表示"""
    
    def run(self):
        """REPLループを実行"""
        print(f"🏛️ AgoraTheon v1.0 - AI討論会システム")
        print(f"📋 討論: {self.discussion.title}")
        print(f"💡 /help でコマンド一覧を表示\n")
        
        while True:
            try:
                line = input("〉")
                output, should_exit = self.process_command(line)
                if output:
                    print(output)
                    print()
                if should_exit:
                    break
            except KeyboardInterrupt:
                print("\n中断しました。/save で保存、/bye で終了")
            except EOFError:
                break


def main():
    parser = argparse.ArgumentParser(description='AgoraTheon - AI討論会システム')
    parser.add_argument('discussion_file', nargs='?', default='discussion.md',
                        help='討論ファイル（.md）')
    parser.add_argument('--data', '-d', action='append', default=[],
                        help='参考資料ファイル（複数指定可）')
    parser.add_argument('--health', action='store_true',
                        help='APIヘルスチェックのみ実行')
    
    args = parser.parse_args()
    
    agora = AgoraTheon(args.discussion_file, args.data)
    
    if args.health:
        print(agora.cmd_health())
        return
    
    agora.run()


if __name__ == '__main__':
    main()
