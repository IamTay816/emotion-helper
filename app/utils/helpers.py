from datetime import datetime
from app.models.mood_entry import MoodLevel


def get_current_date() -> str:
    """获取当前日期字符串 (YYYY-MM-DD)"""
    return datetime.now().strftime('%Y-%m-%d')


def get_current_time() -> str:
    """获取当前时间字符串 (HH:MM)"""
    return datetime.now().strftime('%H:%M')


def get_mood_level(score: int) -> MoodLevel:
    """根据评分获取心情等级"""
    return MoodLevel.get_by_score(score)


def get_mood_options() -> list:
    """获取所有心情选项"""
    return MoodLevel.get_all_options()


def format_date_for_display(date_str: str) -> str:
    """格式化日期用于显示"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        return f"{dt.month}月{dt.day}日 {weekdays[dt.weekday()]}"
    except:
        return date_str


def get_mood_color(score: int) -> str:
    """根据评分获取颜色"""
    if score <= 2:
        return '#FF6B6B'  # 红色
    elif score <= 4:
        return '#FFA07A'  # 橙色
    elif score <= 6:
        return '#FFD93D'  # 黄色
    elif score <= 8:
        return '#6BCB77'  # 绿色
    else:
        return '#4D96FF'  # 蓝色
