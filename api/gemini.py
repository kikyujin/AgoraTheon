"""
Gemini API Wrapper for AgoraTheon
❇️ 実用・高速担当

使用SDK: google-genai (新SDK)
"""

import os
from google import genai
from google.genai import types


class GeminiAPI:
    """Gemini API (Google) - 新SDK版"""
    
    ICON = "❇️"
    NAME = "gemini"
    DISPLAY_NAME = "Gemini"
    
    # キャラクター設定
    SYSTEM_PROMPT = """あなたはAI討論会の参加者「Gemini」です。

## 役割
- 実用的で高速な情報処理を担当
- 最新の情報やデータに基づく議論が得意
- 具体的な解決策や実装案を提示

## 討論での振る舞い
- 効率的に要点をまとめる
- 具体例やデータを交えて説明する
- 実現可能性を重視した提案をする

## 応答スタイル
- 簡潔で実用的
- 必要に応じて箇条書きも使う
- 敬語は使わない（討論参加者として対等）"""
    
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
    
    def generate(self, context: str, prompt: str = "", temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """
        応答を生成
        
        Args:
            context: これまでの討論内容
            prompt: 追加のユーザープロンプト
            temperature: 生成温度
            max_tokens: 最大トークン数
        
        Returns:
            生成された応答
        """
        user_message = self._build_message(context, prompt)
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_PROMPT,
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            return response.text.strip()
        except Exception as e:
            return f"[Gemini エラー] {str(e)}"
    
    def _build_message(self, context: str, prompt: str) -> str:
        """ユーザーメッセージを構築"""
        parts = []
        
        if context:
            parts.append(f"【これまでの討論】\n{context}")
        
        if prompt:
            parts.append(f"【指示】\n{prompt}")
        else:
            parts.append("【指示】\n上記の討論を踏まえて、あなたの見解を述べてください。")
        
        return "\n\n".join(parts)
    
    def health_check(self) -> dict:
        """ヘルスチェック"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Reply with just 'OK'",
                config=types.GenerateContentConfig(max_output_tokens=10)
            )
            return {"status": "healthy", "model": self.model_name}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
