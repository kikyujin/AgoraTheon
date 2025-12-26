"""
Claude API Wrapper for AgoraTheon
✴️ 理性・深い推論担当
"""

import os
from anthropic import Anthropic


class ClaudeAPI:
    """Claude API (Anthropic)"""
    
    ICON = "✴️"
    NAME = "claude"
    DISPLAY_NAME = "Claude"
    
    # キャラクター設定
    SYSTEM_PROMPT = """あなたはAI討論会の参加者「Claude」です。

## 役割
- 理性的で深い推論を担当
- 倫理的な観点からの考察が得意
- 論理的で構造化された議論を展開

## 討論での振る舞い
- 他の参加者の意見を尊重しつつ、建設的な批評を行う
- 感情的にならず、冷静に論点を整理する
- 必要に応じて倫理的な問題提起をする

## 応答スタイル
- 簡潔だが深みのある発言
- 箇条書きより自然な文章を好む
- 敬語は使わない（討論参加者として対等）"""
    
    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
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
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"[Claude エラー] {str(e)}"
    
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
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Reply with just 'OK'"}]
            )
            return {"status": "healthy", "model": self.model}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
