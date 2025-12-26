"""
Sumire Persona - スミレん（司会AI）for AgoraTheon
"""

import os
import requests
from typing import Optional, Tuple


class SumireHost:
    """
    スミレん - AI討論会の司会
    ユーザーの入力を解析し、最適なAIに振り分ける
    """
    
    ICON = "💠"
    NAME = "sumire"
    
    # 振り分け用システムプロンプト
    ROUTING_PROMPT = """あなたは「スミレ」、AI討論会の司会者です。

## 役割
ユーザーの発言や質問を分析し、最も適切なAI参加者に回答を振り分けてください。

## AI参加者の特性
- claude: 理性的で深い推論、倫理的考察、哲学的問題が得意
- gemini: 実用的で高速、最新情報、データ分析、具体的な解決策が得意
- chatgpt: バランスが良い、多角的視点、まとめ役、一般的な質問に対応
- grok: 斬新な視点、ちゃぶ台返し、タブーに切り込む、挑発的な意見が得意

## 出力形式
必ず以下のJSON形式のみで回答してください。他の文章は不要です。

{"target": "AI名", "intro": "スミレんの一言"}

例:
{"target": "claude", "intro": "Claudeさん、倫理的な観点からお願いします"}
{"target": "gemini", "intro": "Geminiさん、最新の情報を踏まえて"}
{"target": "chatgpt", "intro": "ChatGPTさん、バランスよくまとめてください"}
{"target": "grok", "intro": "Grokさん、ちょっと違う視点から切り込んでください"}

## 判断基準
- 倫理、哲学、深い考察 → claude
- 最新情報、データ、実用的な解決策 → gemini
- 一般的な質問、まとめ、バランス → chatgpt
- 挑発的、タブー、斬新な視点 → grok
- 迷ったら → chatgpt
- 直前の発言者には連続で振らない（できれば）

## 注意
- JSON以外の出力は禁止
- 必ず上記4つのAI名のいずれかを選ぶこと"""

    # スミレんの口調用プロンプト
    STYLE_PROMPT = """あなたは「スミレ」です。
一人称は「私」、落ち着いた大人の女性の口調で話します。
簡潔に、でも温かみを持って話してください。"""

    def __init__(self):
        self.backend = os.environ.get('SUMIRE_BACKEND', 'ollama')
        self.ollama_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
        self.ollama_model = os.environ.get('SUMIRE_MODEL', 'gemma3:27b')
    
    def route(self, user_input: str, context: str = "", last_speaker: str = "") -> Tuple[str, str]:
        """
        ユーザー入力を分析して最適なAIを選択
        
        Args:
            user_input: ユーザーの発言
            context: これまでの討論内容
            last_speaker: 直前の発言者（連続回避用）
        
        Returns:
            (target_ai, sumire_intro): 振り分け先AIと紹介文
        """
        
        # 空のenter → 順番に回す or chatgpt
        if not user_input.strip():
            return self._rotate_speaker(last_speaker)
        
        # LLMで振り分け判断
        routing_input = self._build_routing_input(user_input, context, last_speaker)
        
        if self.backend == 'gemini':
            result = self._route_with_gemini(routing_input)
        else:
            result = self._route_with_ollama(routing_input)
        
        return result
    
    def _build_routing_input(self, user_input: str, context: str, last_speaker: str) -> str:
        """振り分け判断用の入力を構築"""
        parts = []
        
        if context:
            # 直近の発言だけ抜粋（長すぎると遅くなる）
            context_lines = context.strip().split('\n')[-10:]
            parts.append(f"【直近の討論】\n" + "\n".join(context_lines))
        
        if last_speaker:
            parts.append(f"【直前の発言者】{last_speaker}（連続回避推奨）")
        
        parts.append(f"【ユーザーの発言】\n{user_input}")
        parts.append("【指示】上記を踏まえて、最適なAIを選び、JSON形式で回答してください。")
        
        return "\n\n".join(parts)
    
    def _route_with_ollama(self, routing_input: str) -> Tuple[str, str]:
        """Ollama (gemma3) で振り分け"""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": routing_input,
                    "system": self.ROUTING_PROMPT,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 200
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            result_text = response.json().get("response", "")
            return self._parse_routing_result(result_text)
        except Exception as e:
            print(f"[Ollama振り分けエラー] {e}")
            return ("chatgpt", "ChatGPTさん、お願いします")
    
    def _route_with_gemini(self, routing_input: str) -> Tuple[str, str]:
        """Gemini で振り分け"""
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=routing_input,
                config=types.GenerateContentConfig(
                    system_instruction=self.ROUTING_PROMPT,
                    temperature=0.3,
                    max_output_tokens=200
                )
            )
            return self._parse_routing_result(response.text)
        except Exception as e:
            print(f"[Gemini振り分けエラー] {e}")
            return ("chatgpt", "ChatGPTさん、お願いします")
    
    def _parse_routing_result(self, result_text: str) -> Tuple[str, str]:
        """LLMの出力をパース"""
        import json
        import re
        
        # JSON部分を抽出
        json_match = re.search(r'\{[^}]+\}', result_text)
        if json_match:
            try:
                data = json.loads(json_match.group())
                target = data.get("target", "chatgpt").lower()
                intro = data.get("intro", "お願いします")
                
                # 有効なターゲットか確認
                valid_targets = ["claude", "gemini", "chatgpt", "grok"]
                if target not in valid_targets:
                    target = "chatgpt"
                
                return (target, intro)
            except json.JSONDecodeError:
                pass
        
        # パース失敗時のフォールバック
        return ("chatgpt", "ChatGPTさん、お願いします")
    
    def _rotate_speaker(self, last_speaker: str) -> Tuple[str, str]:
        """空enterの場合、順番に回す"""
        rotation = ["claude", "gemini", "chatgpt", "grok"]
        intros = {
            "claude": "Claudeさん、いかがでしょうか",
            "gemini": "Geminiさん、お願いします",
            "chatgpt": "ChatGPTさん、どうぞ",
            "grok": "Grokさん、何かありますか"
        }
        
        if last_speaker in rotation:
            idx = rotation.index(last_speaker)
            next_speaker = rotation[(idx + 1) % len(rotation)]
        else:
            next_speaker = "claude"
        
        return (next_speaker, intros[next_speaker])
    
    def health_check(self) -> dict:
        """ヘルスチェック"""
        if self.backend == 'gemini':
            return {"status": "using_gemini", "backend": "gemini"}
        
        try:
            response = requests.get(
                f"{self.ollama_host}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            models = [m["name"] for m in response.json().get("models", [])]
            has_model = any(self.ollama_model in m for m in models)
            
            return {
                "status": "healthy" if has_model else "model_missing",
                "backend": "ollama",
                "host": self.ollama_host,
                "model": self.ollama_model,
                "available": models
            }
        except Exception as e:
            return {"status": "unhealthy", "backend": "ollama", "error": str(e)}
