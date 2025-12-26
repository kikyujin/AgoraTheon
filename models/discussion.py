"""
Discussion Model for AgoraTheon
討論データの構造定義
"""

import json
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Message:
    """1つの発言"""
    id: str
    timestamp: str
    speaker: str  # claude, gemini, chatgpt, grok, sumire, master
    icon: str
    content: str
    filtered: bool = False
    deleted: bool = False
    original_content: Optional[str] = None  # フィルタ前の内容
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(**data)
    
    def display(self) -> str:
        """表示用フォーマット"""
        if self.deleted:
            return ""
        prefix = "*" if self.filtered else ""
        return f"{prefix}{self.icon}{self.speaker}: {self.content}"


@dataclass
class Discussion:
    """討論全体"""
    title: str
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    updated: str = field(default_factory=lambda: datetime.now().isoformat())
    data_files: List[str] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    _next_id: int = field(default=1, repr=False)
    
    def add_message(self, speaker: str, icon: str, content: str) -> Message:
        """発言を追加"""
        msg = Message(
            id=f"{self._next_id:03d}",
            timestamp=datetime.now().isoformat(),
            speaker=speaker,
            icon=icon,
            content=content
        )
        self.messages.append(msg)
        self._next_id += 1
        self.updated = datetime.now().isoformat()
        return msg
    
    def get_last_message(self) -> Optional[Message]:
        """最後の発言を取得（削除済み除く）"""
        for msg in reversed(self.messages):
            if not msg.deleted:
                return msg
        return None
    
    def delete_last(self) -> bool:
        """最後の発言を削除"""
        msg = self.get_last_message()
        if msg:
            msg.deleted = True
            self.updated = datetime.now().isoformat()
            return True
        return False
    
    def filter_last(self, filtered_content: str) -> bool:
        """最後の発言をフィルタリング"""
        msg = self.get_last_message()
        if msg:
            msg.original_content = msg.content
            msg.content = filtered_content
            msg.filtered = True
            self.updated = datetime.now().isoformat()
            return True
        return False
    
    def get_context(self, max_messages: int = 20) -> str:
        """討論コンテキストを文字列で取得"""
        active_messages = [m for m in self.messages if not m.deleted]
        recent = active_messages[-max_messages:] if len(active_messages) > max_messages else active_messages
        
        lines = []
        for msg in recent:
            lines.append(msg.display())
        
        return "\n\n".join(lines)
    
    def to_dict(self) -> dict:
        """辞書に変換"""
        return {
            "title": self.title,
            "created": self.created,
            "updated": self.updated,
            "data_files": self.data_files,
            "messages": [m.to_dict() for m in self.messages],
            "_next_id": self._next_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Discussion":
        """辞書から復元"""
        messages = [Message.from_dict(m) for m in data.get("messages", [])]
        return cls(
            title=data["title"],
            created=data.get("created", datetime.now().isoformat()),
            updated=data.get("updated", datetime.now().isoformat()),
            data_files=data.get("data_files", []),
            messages=messages,
            _next_id=data.get("_next_id", len(messages) + 1)
        )
    
    def to_json(self, indent: int = 2) -> str:
        """JSON文字列に変換"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Discussion":
        """JSON文字列から復元"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def to_markdown(self) -> str:
        """Markdown形式に変換"""
        lines = [f"# {self.title}", ""]
        
        if self.data_files:
            lines.append("## 参考資料")
            for f in self.data_files:
                lines.append(f"- {f}")
            lines.append("")
        
        lines.append("## 討論内容")
        lines.append("")
        
        for msg in self.messages:
            if msg.deleted:
                continue
            prefix = "*" if msg.filtered else ""
            lines.append(f"{prefix}{msg.icon}{msg.speaker}: {msg.content}")
            lines.append("")
        
        return "\n".join(lines)
    
    @classmethod
    def from_markdown(cls, md_str: str, title: str = "Untitled") -> "Discussion":
        """Markdown形式から復元（簡易パーサー）"""
        from ..api import ICONS
        
        discussion = cls(title=title)
        
        # アイコンから話者を逆引き
        icon_to_speaker = {v: k for k, v in ICONS.items()}
        
        lines = md_str.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # タイトル行
            if line.startswith("# "):
                discussion.title = line[2:].strip()
                continue
            
            # 発言行を検出
            filtered = line.startswith("*")
            if filtered:
                line = line[1:]
            
            for icon, speaker in icon_to_speaker.items():
                if line.startswith(icon):
                    # アイコン + speaker: content の形式
                    rest = line[len(icon):]
                    if rest.startswith(speaker + ":"):
                        content = rest[len(speaker) + 1:].strip()
                        msg = discussion.add_message(speaker, icon, content)
                        msg.filtered = filtered
                        break
        
        return discussion
