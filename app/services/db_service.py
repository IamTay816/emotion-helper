import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'emoodie_db.sqlite')



class DatabaseService:
    """数据库服务类，负责所有数据库操作"""

    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()

    def connect(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.connection = sqlite3.connect(DB_PATH)
        self.connection.row_factory = sqlite3.Row
        print(f"数据库已连接: {DB_PATH}")

    def create_tables(self):
        cursor = self.connection.cursor()

        # 心情记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time_slot TEXT,
                score INTEGER NOT NULL CHECK(score >= 1 AND score <= 10),
                emoji TEXT NOT NULL,
                mood_label TEXT NOT NULL,
                note TEXT,
                record_type TEXT NOT NULL CHECK(record_type IN ('daily', 'slot')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # 每日总结表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                summary_text TEXT,
                avg_score REAL,
                dominant_emoji TEXT,
                generated_at TEXT NOT NULL,
                is_auto BOOLEAN DEFAULT 0
            )
        ''')

        # 对话会话表（新增）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # 对话消息表（改造：关联到会话）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
            )
        ''')

        # 应用设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT NOT NULL
            )
        ''')

        self.connection.commit()
        print("数据表创建完成")

    def insert_mood_entry(self, entry: dict) -> int:
        """插入一条心情记录，同一日期+同一时间段只保留最新的一条"""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()

        # 先去重
        cursor.execute('''
            DELETE FROM mood_entries
            WHERE date = ? AND time_slot = ? AND record_type = ?
        ''', (
            entry['date'],
            entry.get('time_slot'),
            entry['record_type']
        ))

        # 再插入
        cursor.execute('''
            INSERT INTO mood_entries (date, time_slot, score, emoji, mood_label, note, record_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry['date'],
            entry.get('time_slot'),
            entry['score'],
            entry['emoji'],
            entry['mood_label'],
            entry.get('note'),
            entry['record_type'],
            now,
            now
        ))
        self.connection.commit()
        return cursor.lastrowid

    def get_daily_mood_entries(self, date: str) -> List[Dict]:
        """获取某一天的所有心情记录"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM mood_entries
            WHERE date = ?
            ORDER BY time_slot ASC
        ''', (date,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_all_mood_entries(self, limit: int = 500) -> List[Dict]:
        """获取所有心情记录（按日期倒序）"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM mood_entries
            ORDER BY date DESC, time_slot DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def insert_daily_summary(self, summary: dict) -> int:
        """插入每日总结"""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO daily_summaries (date, summary_text, avg_score, dominant_emoji, generated_at, is_auto)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            summary['date'],
            summary.get('summary_text'),
            summary.get('avg_score'),
            summary.get('dominant_emoji'),
            now,
            summary.get('is_auto', False)
        ))
        self.connection.commit()
        return cursor.lastrowid

    def get_daily_summary(self, date: str) -> Optional[Dict]:
        """获取某一天的总结"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM daily_summaries WHERE date = ?
        ''', (date,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # ===== 对话会话相关方法 =====

    def create_session(self, title: str) -> int:
        """创建新对话会话，返回会话ID"""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO chat_sessions (title, created_at, updated_at)
            VALUES (?, ?, ?)
        ''', (title, now, now))
        self.connection.commit()
        return cursor.lastrowid

    def get_all_sessions(self) -> List[Dict]:
        """获取所有会话（按更新时间倒序）"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM chat_sessions
            ORDER BY updated_at DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_session_messages(self, session_id: int) -> List[Dict]:
        """获取指定会话的所有消息"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM chat_messages
            WHERE session_id = ?
            ORDER BY created_at ASC
        ''', (session_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def add_message(self, session_id: int, role: str, content: str) -> int:
        """向指定会话添加消息"""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO chat_messages (session_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
        ''', (session_id, role, content, now))
        # 更新会话的最后更新时间
        cursor.execute('''
            UPDATE chat_sessions SET updated_at = ? WHERE id = ?
        ''', (now, session_id))
        self.connection.commit()
        return cursor.lastrowid

    def delete_session(self, session_id: int):
        """删除会话及其所有消息"""
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
        self.connection.commit()

    def delete_all_sessions(self):
        """删除所有会话（用于数据迁移）"""
        cursor = self.connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS chat_messages')
        cursor.execute('DROP TABLE IF EXISTS chat_sessions')
        self.connection.commit()

    # ===== 旧方法兼容（保留以防其他地方还在用） =====

    def insert_chat_message(self, message: dict) -> int:
        """兼容旧接口：插入对话记录"""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO chat_history (date, user_message, ai_response, mood_before, mood_after, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            message['date'],
            message.get('user_message', ''),
            message.get('ai_response', ''),
            message.get('mood_before'),
            message.get('mood_after'),
            now
        ))
        self.connection.commit()
        return cursor.lastrowid

    def get_chat_history(self, date: str) -> List[Dict]:
        """兼容旧接口：获取某一天的对话历史"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM chat_history
            WHERE date = ?
            ORDER BY created_at ASC
        ''', (date,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def save_setting(self, key: str, value: str):
        """保存应用设置"""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO app_settings (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, now))
        self.connection.commit()

    def get_setting(self, key: str) -> Optional[str]:
        """获取应用设置"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT value FROM app_settings WHERE key = ?
        ''', (key,))
        row = cursor.fetchone()
        return row['value'] if row else None

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("数据库已关闭")


# 全局单例
db_service = DatabaseService()
