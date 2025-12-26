"""
AgoraTheon API Wrappers
"""

from .claude import ClaudeAPI
from .gemini import GeminiAPI
from .chatgpt import ChatGPTAPI
from .grok import GrokAPI

# 全APIクラスのマッピング
API_MAP = {
    "claude": ClaudeAPI,
    "gemini": GeminiAPI,
    "chatgpt": ChatGPTAPI,
    "grok": GrokAPI,
}

# アイコンマッピング
ICONS = {
    "claude": "✴️",
    "gemini": "❇️",
    "chatgpt": "♻️",
    "grok": "♨️",
    "sumire": "💠",
}

__all__ = [
    "ClaudeAPI",
    "GeminiAPI", 
    "ChatGPTAPI",
    "GrokAPI",
    "API_MAP",
    "ICONS",
]
