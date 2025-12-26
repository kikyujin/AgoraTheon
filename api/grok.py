"""
Grok API Wrapper for AgoraTheon
♨️ 叡智・ちゃぶ台返し担当
"""

import os
from openai import OpenAI


class GrokAPI:
    """Grok API (xAI) - OpenAI互換インターフェース"""
    
    ICON = "♨️"
    NAME = "grok"
    DISPLAY_NAME = "Grok"
    
    # キャラクター設定
    SYSTEM_PROMPT = """あなたはAI討論会の参加者「Grok」です。

## 役割
- イーロンの引用とちゃぶ台返しを担当
- 既存の議論をひっくり返す斬新な視点を提供
- タブーや常識を恐れない発言

## 討論での振る舞い
- 他の参加者が見落としている視点を指摘
- 皮肉やユーモアを交えた発言
- 時に挑発的だが、本質を突く

## 応答スタイル
- 率直で遠慮がない
- 知的だがカジュアル
- 敬語は使わない（討論参加者として対等）
- イーロン・マスクの引用はポイントを押さえて使用"""
    
    def __init__(self):
        api_key = os.environ.get('GROK_API_KEY')
        if not api_key:
            raise ValueError("GROK_API_KEY not set")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        self.model = "grok-3-fast"
    
    def generate(self, context: str, prompt: str = "", temperature: float = 0.8, max_tokens: int = 2048) -> str:
        """
        応答を生成
        
        Args:
            context: これまでの討論内容
            prompt: 追加のユーザープロンプト
            temperature: 生成温度（Grokは少し高め）
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
            return f"[Grok エラー] {str(e)}"
    
    def _build_message(self, context: str, prompt: str) -> str:
        """ユーザーメッセージを構築"""
        parts = []
        
        if context:
            parts.append(f"【これまでの討論】\n{context}")
        
        if prompt:
            parts.append(f"【指示】\n{prompt}")
        else:
            parts.append("【指示】\n上記の討論を踏まえて、ちゃぶ台返しの視点で見解を述べてください。")
        
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
