import random
from typing import List, Dict
from app.services.db_service import db_service


class ChatEngine:
    """本地对话引擎，基于规则回应"""
    
    # 情绪关键词
    NEGATIVE_KEYWORDS = ['难过', '伤心', '委屈', '愤怒', '烦躁', '焦虑', '压力大', '累', '烦', 
                        '无助', '孤独', '失望', '沮丧', '痛苦', '害怕', '担心', '困惑', '不好']
    
    POSITIVE_KEYWORDS = ['开心', '高兴', '快乐', '满足', '感恩', '顺利', '感谢', '不错', 
                        '棒', '好', '幸福', '温暖', '轻松', '平静', '期待', '兴奋']
    
    # 共情回应库
    EMPATHY_RESPONSES = [
        "我理解你的感受，这种情绪是很正常的。",
        "听起来你经历了一段不容易的时光，辛苦了。",
        "你的感受很重要，谢谢你愿意分享给我。",
        "我能感受到你现在的心情不太好，没关系，我在这里陪你。",
        "每个人都会遇到这样的时刻，你已经很棒了。",
    ]
    
    # 引导提问库
    GUIDING_QUESTIONS = [
        "能跟我多说说是怎么回事吗？",
        "这件事是从什么时候开始让你感到困扰的？",
        "你觉得是什么触发了这样的感受？",
        "除了这件事，最近还有其他让你在意的事情吗？",
    ]
    
    # 放松建议库
    RELAXATION_TIPS = [
        "试试深呼吸：吸气4秒，屏住4秒，呼气4秒，重复几次，感受身体慢慢放松。",
        "喝一杯温水，让身体先放松下来。",
        "离开现在的环境，出去走走，呼吸新鲜空气。",
        "听一首你喜欢的歌，让音乐帮助你平复心情。",
        "找个安静的地方，闭上眼睛，专注于自己的呼吸。",
    ]
    
    # 积极鼓励库
    ENCOURAGEMENTS = [
        "你已经在努力了，这本身就值得肯定。",
        "相信自己，你有能力度过这个难关。",
        "每一次面对情绪的勇气，都在让你变得更强大。",
        "慢慢来，不需要一下子解决所有问题。",
        "无论发生什么，都要记得对自己温柔一点。",
    ]
    
    # 正面回应库
    POSITIVE_RESPONSES = [
        "听到你心情这么好，我也很开心！继续保持这份好心情～",
        "太棒了！看来今天对你来说是个好日子呢！",
        "你的积极心态真的很感染人，愿这份快乐一直陪伴着你！",
    ]
    
    def generate_response(self, user_message: str, mood_before: int = None) -> Dict:
        """根据用户消息生成AI回应"""
        # 判断情绪倾向
        sentiment = self._detect_sentiment(user_message)
        
        # 构建回应
        if sentiment == 'negative':
            response = self._generate_negative_response(user_message, mood_before)
        elif sentiment == 'positive':
            response = self._generate_positive_response(user_message)
        else:
            response = self._generate_neutral_response(user_message)
        
        return {
            'response': response,
            'sentiment': sentiment,
        }
    
    def _detect_sentiment(self, message: str) -> str:
        """检测消息的情绪倾向"""
        negative_count = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in message)
        positive_count = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in message)
        
        if negative_count > positive_count:
            return 'negative'
        elif positive_count > negative_count:
            return 'positive'
        else:
            return 'neutral'
    
    def _generate_negative_response(self, message: str, mood_before: int = None) -> str:
        """生成负面情绪的回应"""
        parts = []
        
        # 共情
        parts.append(random.choice(self.EMPATHY_RESPONSES))
        
        # 引导提问（适当时候）
        if len(message) > 5:
            parts.append(random.choice(self.GUIDING_QUESTIONS))
        
        # 放松建议
        parts.append(random.choice(self.RELAXATION_TIPS))
        
        # 鼓励
        parts.append(random.choice(self.ENCOURAGEMENTS))
        
        return "\n".join(parts)
    
    def _generate_positive_response(self, message: str) -> str:
        """生成正面情绪的回应"""
        return random.choice(self.POSITIVE_RESPONSES)
    
    def _generate_neutral_response(self, message: str) -> str:
        """生成中性情绪的回应"""
        neutral_responses = [
            "我听到了，谢谢你跟我分享。如果想多说点什么，我都在这里。",
            "平淡的日子也是一种幸福呢。有什么想聊的吗？",
            "有时候生活就是这样，不急不缓。你现在的感受是怎样的？",
            "没关系，不想说也没事。我就在这里陪着你。",
        ]
        return random.choice(neutral_responses)
    
    def save_chat(self, user_message: str, ai_response: str, 
                 mood_before: int = None, mood_after: int = None):
        """保存对话记录到数据库"""
        from datetime import datetime
        
        chat_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'user_message': user_message,
            'ai_response': ai_response,
            'mood_before': mood_before,
            'mood_after': mood_after,
        }
        db_service.insert_chat_message(chat_data)
