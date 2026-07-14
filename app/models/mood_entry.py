from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MoodLevel(Enum):
    """心情等级枚举"""
    VERY_BAD = ("very_bad", 1, 2, "😫", "非常糟糕")
    BAD = ("bad", 3, 4, "😔", "比较糟糕")
    NEUTRAL = ("neutral", 5, 6, "😐", "一般")
    GOOD = ("good", 7, 8, "🙂", "比较愉快")
    VERY_GOOD = ("very_good", 9, 10, "😊", "非常愉快")
    
    def __init__(self, key: str, min_score: int, max_score: int, emoji: str, label: str):
        self.key = key
        self.min_score = min_score
        self.max_score = max_score
        self.emoji = emoji
        self.label = label
    
    @classmethod
    def get_by_score(cls, score: int) -> 'MoodLevel':
        """根据评分获取心情等级"""
        for level in cls:
            if level.min_score <= score <= level.max_score:
                return level
        return cls.NEUTRAL
    
    @classmethod
    def get_all_options(cls) -> list:
        """获取所有心情选项"""
        return [
            {"score_range": "1-2", "emoji": "😫", "label": "非常糟糕", "level": cls.VERY_BAD},
            {"score_range": "3-4", "emoji": "😔", "label": "比较糟糕", "level": cls.BAD},
            {"score_range": "5-6", "emoji": "😐", "label": "一般", "level": cls.NEUTRAL},
            {"score_range": "7-8", "emoji": "🙂", "label": "比较愉快", "level": cls.GOOD},
            {"score_range": "9-10", "emoji": "😊", "label": "非常愉快", "level": cls.VERY_GOOD},
        ]


@dataclass
class MoodEntry:
    """心情记录数据模型"""
    date: str
    score: int
    emoji: str
    mood_label: str
    note: Optional[str] = None
    time_slot: Optional[str] = None
    record_type: str = "daily"  # 'daily' or 'slot'
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'date': self.date,
            'time_slot': self.time_slot,
            'score': self.score,
            'emoji': self.emoji,
            'mood_label': self.mood_label,
            'note': self.note,
            'record_type': self.record_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MoodEntry':
        """从字典创建实例"""
        return cls(
            id=data.get('id'),
            date=data['date'],
            time_slot=data.get('time_slot'),
            score=data['score'],
            emoji=data['emoji'],
            mood_label=data['mood_label'],
            note=data.get('note'),
            record_type=data.get('record_type', 'daily'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )


@dataclass
class ChatMessage:
    """对话消息数据模型"""
    date: str
    user_message: str
    ai_response: str
    mood_before: Optional[int] = None
    mood_after: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'date': self.date,
            'user_message': self.user_message,
            'ai_response': self.ai_response,
            'mood_before': self.mood_before,
            'mood_after': self.mood_after,
            'created_at': self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChatMessage':
        """从字典创建实例"""
        return cls(
            id=data.get('id'),
            date=data['date'],
            user_message=data['user_message'],
            ai_response=data['ai_response'],
            mood_before=data.get('mood_before'),
            mood_after=data.get('mood_after'),
            created_at=data.get('created_at'),
        )
