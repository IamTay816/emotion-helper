from typing import List, Dict, Optional
from datetime import datetime
from collections import Counter
from app.services.db_service import db_service


class MoodAnalyzer:
    """情绪分析服务，负责生成每日情绪总结"""
    
    # 情绪关键词词典
    NEGATIVE_KEYWORDS = {
        '难过', '伤心', '委屈', '愤怒', '烦躁', '焦虑', '压力大', '累', '烦', 
        '无助', '孤独', '失望', '沮丧', '痛苦', '害怕', '担心', '困惑'
    }
    
    POSITIVE_KEYWORDS = {
        '开心', '高兴', '快乐', '满足', '感恩', '顺利', '感谢', '不错', 
        '棒', '好', '幸福', '温暖', '轻松', '平静', '期待', '兴奋'
    }
    
    # 情绪总结模板
    SUMMARY_TEMPLATES = {
        'good': [
            "今天的心情很不错呢！{emoji} 从记录来看，你的平均评分达到了{avg_score:.1f}分。",
            "看到你今天的心情这么好，真为你高兴！{emoji} 整体表现很积极。",
        ],
        'neutral': [
            "今天的心情比较平稳，{emoji} 平均评分{avg_score:.1f}分，属于正常范围。",
            "今天过得平平淡淡，{emoji} 评分{avg_score:.1f}分，保持这样的节奏就好。",
        ],
        'bad': [
            "今天的心情似乎有些低落，{emoji} 平均评分{avg_score:.1f}分，记得照顾好自己哦。",
            "看到你今天不太开心，{emoji} 评分{avg_score:.1f}分，别太勉强自己。",
        ],
    }
    
    def analyze_daily_mood(self, date: str) -> Optional[Dict]:
        """分析某一天的情绪并生成总结"""
        # 获取当天的所有记录
        entries = db_service.get_daily_mood_entries(date)
        
        if not entries:
            return None
        
        # 计算统计数据
        scores = [e['score'] for e in entries]
        avg_score = sum(scores) / len(scores)
        
        # 统计表情分布
        emojis = [e['emoji'] for e in entries]
        dominant_emoji = Counter(emojis).most_common(1)[0][0]
        
        # 统计情绪标签分布
        labels = [e['mood_label'] for e in entries]
        dominant_label = Counter(labels).most_common(1)[0][0]
        
        # 分析备注中的关键词
        notes = [e.get('note', '') for e in entries if e.get('note')]
        keyword_analysis = self._analyze_keywords(notes)
        
        # 计算情绪波动
        score_variance = max(scores) - min(scores) if scores else 0
        
        # 生成总结文本
        summary_text = self._generate_summary(
            avg_score, dominant_emoji, dominant_label, 
            keyword_analysis, score_variance, len(entries)
        )
        
        # 保存总结到数据库
        summary_data = {
            'date': date,
            'summary_text': summary_text,
            'avg_score': avg_score,
            'dominant_emoji': dominant_emoji,
            'is_auto': True,
        }
        db_service.insert_daily_summary(summary_data)
        
        return {
            'date': date,
            'summary_text': summary_text,
            'avg_score': avg_score,
            'dominant_emoji': dominant_emoji,
            'dominant_label': dominant_label,
            'keyword_analysis': keyword_analysis,
            'score_variance': score_variance,
            'total_records': len(entries),
        }
    
    def _analyze_keywords(self, notes: List[str]) -> Dict:
        """分析备注中的关键词"""
        negative_count = 0
        positive_count = 0
        found_keywords = []
        
        for note in notes:
            for keyword in self.NEGATIVE_KEYWORDS:
                if keyword in note:
                    negative_count += 1
                    found_keywords.append((keyword, 'negative'))
            for keyword in self.POSITIVE_KEYWORDS:
                if keyword in note:
                    positive_count += 1
                    found_keywords.append((keyword, 'positive'))
        
        return {
            'negative_count': negative_count,
            'positive_count': positive_count,
            'keywords': found_keywords,
        }
    
    def _generate_summary(self, avg_score: float, dominant_emoji: str, 
                         dominant_label: str, keyword_analysis: Dict, 
                         score_variance: int, total_records: int) -> str:
        """生成情绪总结文本"""
        lines = []
        
        # 开场白
        if avg_score >= 7:
            category = 'good'
        elif avg_score >= 5:
            category = 'neutral'
        else:
            category = 'bad'
        
        template = self.SUMMARY_TEMPLATES[category][0]
        lines.append(template.format(
            emoji=dominant_emoji, 
            avg_score=avg_score
        ))
        
        # 详细分析
        lines.append(f"\n📊 今日共有 {total_records} 条记录")
        
        if score_variance <= 2:
            lines.append("💭 今天的情绪比较稳定，没有太大波动。")
        elif score_variance <= 5:
            lines.append("💭 今天的情绪有一定波动，可能有事情影响了你的心情。")
        else:
            lines.append("💭 今天的情绪起伏比较大，经历了明显的高低变化。")
        
        # 关键词分析
        if keyword_analysis['keywords']:
            neg_kws = [kw for kw, _ in keyword_analysis['keywords'] if _ == 'negative']
            pos_kws = [kw for kw, _ in keyword_analysis['keywords'] if _ == 'positive']
            
            if neg_kws:
                lines.append(f"🔍 注意到的关键词：{', '.join(set(neg_kws))}")
            if pos_kws:
                lines.append(f"✨ 积极关键词：{', '.join(set(pos_kws))}")
        
        # 温馨提示
        lines.append("\n---")
        if avg_score >= 7:
            lines.append("💪 继续保持这样的好心情！适当的运动和良好的作息会让你的状态更佳。")
        elif avg_score >= 5:
            lines.append("🌟 今天过得还不错！试着找一件让自己开心的小事，让心情更好一点。")
        else:
            lines.append("🤗 今天辛苦了！记住，情绪低落是正常的，给自己一些时间和空间。深呼吸，慢慢来。")
        
        return "\n".join(lines)
    
    def generate_summary_manually(self, date: str) -> Optional[Dict]:
        """手动生成指定日期的总结"""
        # 先删除已有的自动总结
        # 重新分析
        return self.analyze_daily_mood(date)
