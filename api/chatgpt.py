"""
ChatGPT API Wrapper for AgoraTheon
♻️ 汎用・バランス担当
"""

import os
from openai import OpenAI


class ChatGPTAPI:
    """ChatGPT API (OpenAI)"""
    
    ICON = "♻️"
    NAME = "chatgpt"
    DISPLAY_NAME = "ChatGPT"
    
    # キャラクター設定
    SYSTEM_PROMPT = """あなたはAI討論会の参加者「ChatGPT」です。

## 役割
- 汎用的でバランスの取れた議論を担当
- 多角的な視点から意見を述べる
- 異なる立場を橋渡しする調整役

## 討論での振る舞い
- 偏りのない中立的な視点を提供
- 他の参加者の意見を統合・発展させる
- 議論の抜け漏れを補完する

## 応答スタイル
- バランスが取れた表現
- 複数の視点を提示することもある
- 敬語は使わない（討論参加者として対等）"""
    
    def __init__(self):
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"
    
    def generate(self, context: str, prompt: str = "", temperature: float = 0.7, max_tokens: int = 1024) -> str:
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[ChatGPT エラー] {str(e)}"
    
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Reply with just 'OK'"}],
                max_tokens=10
            )
            return {"status": "healthy", "model": self.model}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
