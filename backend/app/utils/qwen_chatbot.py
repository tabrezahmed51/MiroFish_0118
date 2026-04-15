"""
Qwen AI Chatbot Client for Smart-Talk Framework
专门用于印度风格开放式讨论的 Qwen AI 模型客户端
支持多语言（印地语、英语）和多情感模式
"""

import json
import re
from typing import Optional, Dict, Any, List
from openai import OpenAI

from ..config import Config


class QwenChatbotClient:
    """
    Qwen AI Chatbot 客户端
    专门为 Smart-Talk 框架设计，支持印度风格对话
    """
    
    # Smart-Talk 情感模式系统提示词
    EMOTIONAL_MODES = {
        "angry": {
            "en": "You are an Indian person expressing angry opinions. Use passionate, heated language typical of Indian debates. Reference Indian context like cricket matches, politics, or traffic.",
            "hi": "आप एक गुस्सैल भारतीय व्यक्ति हैं जो क्रिकेट मैच, राजनीति या ट्रैफिक जैसे भारतीय संदर्भों का उपयोग करके गुस्से में बहस कर रहे हैं।"
        },
        "cricket_excitement": {
            "en": "You are an excited Indian cricket fan. Use emotional, passionate language about cricket matches, players like Virat Kohli, Rohit Sharma. Express joy, disappointment, or excitement.",
            "hi": "आप एक उत्साहित भारतीय क्रिकेट प्रशंसक हैं। विराट कोहली, रोहित शर्मा जैसे खिलाड़ियों के बारे में भावनात्मक भाषा का प्रयोग करें।"
        },
        "budget_discussion": {
            "en": "You are an Indian citizen discussing the Union Budget. Talk about taxes, middle-class concerns, farmer issues, with typical Indian perspective.",
            "hi": "आप केंद्रीय बजट पर चर्चा करने वाले एक भारतीय नागरिक हैं। कर, मध्यम वर्ग की चिंताओं, किसानों की समस्याओं के बारे में बात करें।"
        },
        "festival_happy": {
            "en": "You are a happy Indian celebrating festivals like Diwali, Holi, Eid, Christmas. Share joy, traditions, family gatherings, food, and cultural richness.",
            "hi": "आप दिवाली, होली, ईद, क्रिसमस जैसे त्योहार मना रहे खुश भारतीय हैं। खुशी, परंपराओं, पारिवारिक समारोहों को साझा करें।"
        },
        "family_devastation": {
            "en": "You are an Indian person dealing with family tragedy or crisis. Express deep emotions, family values, community support typical in Indian culture.",
            "hi": "आप पारिवारिक दुख या संकट से जूझ रहे भारतीय व्यक्ति हैं। गहरी भावनाओं, पारिवारिक मूल्यों को व्यक्त करें।"
        },
        "betrayal_sadness": {
            "en": "You are sad due to betrayal by a friend or loved one. Express emotions in an Indian context where relationships are highly valued.",
            "hi": "आप किसी दोस्त या प्रियजन द्वारा धोखा देने के कारण दुखी हैं। भारतीय संदर्भ में भावनाओं को व्यक्त करें जहां रिश्तों को उच्च महत्व दिया जाता है।"
        },
        "mourning": {
            "en": "You are in mourning period. Express grief respectfully, referencing Indian mourning customs and spiritual beliefs.",
            "hi": "आप शोक की अवधि में हैं। भारतीय शोक रीति-रिवाजों और आध्यात्मिक मान्यताओं का उल्लेख करते हुए सम्मानपूर्वक दुख व्यक्त करें।"
        }
    }
    
    # Topic-specific knowledge
    TOPICS = {
        "sensex": "Indian stock market (BSE Sensex), investments, trading, economic trends",
        "elections": "Indian elections, politics, democracy, voting, political parties",
        "investments": "Investment options in India - stocks, mutual funds, gold, real estate, FD",
        "business": "Indian business, startups, entrepreneurship, MSME, corporate sector",
        "sports": "Indian sports - cricket, hockey, football, Olympics, athletes",
        "weather_raining": "Monsoon season in India, rainfall, agriculture impact",
        "weather_drizzling": "Light rain, pleasant weather, chai-pakoda mood",
        "weather_sunny": "Hot summer days, heat waves, summer activities",
        "weather_cloudy": "Cloudy skies, pre-monsoon atmosphere",
        "season_winter": "Winter season in India, cold weather, winter festivals",
        "season_monsoon": "Monsoon season, rains, greenery, farming",
        "season_summer": "Summer season, heat, vacations, mangoes",
        "season_autumn": "Autumn/fall season, harvest festivals, pleasant weather"
    }
    
    # Age group adaptations
    AGE_GROUPS = {
        "teenage": "Speak like an Indian teenager - use slang, reference studies, exams, social media, cricket, Bollywood",
        "student_postgrad": "Speak like an Indian post-graduate student - career concerns, higher education, job market",
        "millennial": "Speak like an Indian millennial - work-life balance, startup culture, modern vs traditional values",
        "senior_citizen": "Speak like an Indian senior citizen - traditional values, family wisdom, nostalgia, health concerns"
    }
    
    # Gender perspectives (culturally sensitive)
    GENDER_PERSPECTIVES = {
        "male": "Male perspective in Indian society - traditional and modern views",
        "female": "Female perspective in Indian society - empowerment, challenges, achievements",
        "transgender": "Transgender perspective in Indian society - inclusivity, struggles, pride",
        "other": "Inclusive perspective respecting all gender identities"
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.QWEN_API_KEY or Config.LLM_API_KEY
        self.base_url = base_url or Config.QWEN_BASE_URL or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = model or Config.QWEN_MODEL_NAME or "qwen-plus"
        
        if not self.api_key:
            raise ValueError("QWEN_API_KEY or LLM_API_KEY 未配置")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def _build_system_prompt(
        self,
        mode: str = "neutral",
        topic: Optional[str] = None,
        weather: Optional[str] = None,
        season: Optional[str] = None,
        age_group: Optional[str] = None,
        gender: Optional[str] = None,
        language: str = "hi"
    ) -> str:
        """
        构建 Smart-Talk 系统提示词
        
        Args:
            mode: 情感模式 (angry, cricket_excitement, budget_discussion, etc.)
            topic: 话题 (sensex, elections, investments, etc.)
            weather: 天气 (raining, drizzling, sunny, cloudy)
            season: 季节 (winter, monsoon, summer, autumn)
            age_group: 年龄组 (teenage, student_postgrad, millennial, senior_citizen)
            gender: 性别视角 (male, female, transgender, other)
            language: 语言 (hi=हिंदी, en=English)
            
        Returns:
            完整的系统提示词
        """
        prompts = []
        
        # 基础角色设定
        prompts.append("You are participating in 'Smart-Talk' - an Indian-style open discussion platform.")
        prompts.append("Respond naturally as an Indian person would, using cultural context, Hindi words mixed with English (Hinglish) when appropriate.")
        
        # 情感模式
        if mode in self.EMOTIONAL_MODES:
            mode_prompt = self.EMOTIONAL_MODES[mode].get(language, self.EMOTIONAL_MODES[mode]["en"])
            prompts.append(f"Current emotional mode: {mode_prompt}")
        
        # 话题
        if topic and topic in self.TOPICS:
            prompts.append(f"Discussion topic: {self.TOPICS[topic]}. Share opinions and insights relevant to Indian context.")
        
        # 天气影响
        if weather:
            weather_prompts = {
                "raining": "It's raining - this might affect mood, reference monsoon, chai, pakoras",
                "drizzling": "Light drizzling - pleasant mood, romantic or relaxed atmosphere",
                "sunny": "Sunny day - hot weather, summer vibes, energetic or tired depending on context",
                "cloudy": "Cloudy day - thoughtful mood, pre-monsoon feeling"
            }
            if weather in weather_prompts:
                prompts.append(f"Weather context: {weather_prompts[weather]}")
        
        # 季节影响
        if season:
            season_prompts = {
                "winter": "Winter season - cold weather, warm clothes, winter festivals, morning fog",
                "monsoon": "Monsoon season - heavy rains, humidity, greenery, farming season",
                "summer": "Summer season - heat, vacations, mangoes, cool drinks",
                "autumn": "Autumn season - harvest time, pleasant weather, festivals"
            }
            if season in season_prompts:
                prompts.append(f"Seasonal context: {season_prompts[season]}")
        
        # 年龄组适配
        if age_group and age_group in self.AGE_GROUPS:
            prompts.append(f"Age group perspective: {self.AGE_GROUPS[age_group]}")
        
        # 性别视角
        if gender and gender in self.GENDER_PERSPECTIVES:
            prompts.append(f"Gender perspective: {self.GENDER_PERSPECTIVES[gender]}")
        
        # 语言设置
        if language == "hi":
            prompts.append("Respond primarily in Hindi (हिंदी), but you can use English words when natural (Hinglish style).")
        elif language == "en-IN":
            prompts.append("Respond in Indian English - use Indian expressions, cultural references, and occasional Hindi words.")
        else:
            prompts.append("Respond in English with Indian cultural context.")
        
        # 文化指导原则
        prompts.append("\nImportant guidelines:")
        prompts.append("- Be respectful of Indian diversity (religion, caste, region, language)")
        prompts.append("- Use Indian examples, references, and cultural context")
        prompts.append("- Avoid stereotypes but embrace cultural richness")
        prompts.append("- Be inclusive and sensitive to all communities")
        prompts.append("- Express opinions passionately but respectfully, as Indians do in discussions")
        
        return "\n".join(prompts)
    
    def chat(
        self,
        user_message: str,
        mode: str = "neutral",
        topic: Optional[str] = None,
        weather: Optional[str] = None,
        season: Optional[str] = None,
        age_group: Optional[str] = None,
        gender: Optional[str] = None,
        language: str = "hi",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.8,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Smart-Talk 聊天接口
        
        Args:
            user_message: 用户消息
            mode: 情感模式
            topic: 话题
            weather: 天气
            season: 季节
            age_group: 年龄组
            gender: 性别视角
            language: 语言 (hi, en-IN, en)
            conversation_history: 对话历史
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Returns:
            包含回复和元数据的字典
        """
        system_prompt = self._build_system_prompt(
            mode=mode,
            topic=topic,
            weather=weather,
            season=season,
            age_group=age_group,
            gender=gender,
            language=language
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history[-10:])  # 保留最近 10 条消息
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            assistant_message = response.choices[0].message.content
            # 清理可能的<think>标签
            assistant_message = re.sub(r'<think>[\s\S]*?</think>', '', assistant_message).strip()
            
            return {
                "success": True,
                "message": assistant_message,
                "mode": mode,
                "topic": topic,
                "language": language,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "क्षमा करें, कुछ त्रुटि हुई। कृपया पुनः प्रयास करें। (Sorry, an error occurred. Please try again.)"
            }
    
    def quick_chat(
        self,
        user_message: str,
        preset: str = "casual",
        language: str = "hi"
    ) -> Dict[str, Any]:
        """
        快速聊天接口 - 使用预设配置
        
        Presets:
        - casual: 随意聊天
        - cricket: 板球讨论
        - budget: 预算讨论
        - festival: 节日庆祝
        - serious: 严肃话题
        """
        presets = {
            "casual": {"mode": "neutral", "topic": None},
            "cricket": {"mode": "cricket_excitement", "topic": "sports"},
            "budget": {"mode": "budget_discussion", "topic": "elections"},
            "festival": {"mode": "festival_happy", "topic": None},
            "serious": {"mode": "neutral", "topic": "sensex"}
        }
        
        config = presets.get(preset, presets["casual"])
        
        return self.chat(
            user_message=user_message,
            mode=config["mode"],
            topic=config["topic"],
            language=language
        )
