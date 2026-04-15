"""
Smart-Talk Chatbot API Routes
印度风格开放式讨论聊天机器人 API
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any

from ..utils.qwen_chatbot import QwenChatbotClient
from ..utils.logger import get_logger

chatbot_bp = Blueprint('chatbot', __name__)
logger = get_logger('mirofish.chatbot')

# 全局客户端实例（延迟初始化）
_chatbot_client = None


def get_chatbot_client() -> QwenChatbotClient:
    """获取或创建 Chatbot 客户端实例"""
    global _chatbot_client
    if _chatbot_client is None:
        _chatbot_client = QwenChatbotClient()
    return _chatbot_client


@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """
    Smart-Talk 聊天接口
    
    Request Body:
    {
        "message": "用户消息",
        "mode": "angry|cricket_excitement|budget_discussion|festival_happy|family_devastation|betrayal_sadness|mourning|neutral",
        "topic": "sensex|elections|investments|business|sports|weather_raining|weather_drizzling|weather_sunny|weather_cloudy|season_winter|season_monsoon|season_summer|season_autumn",
        "weather": "raining|drizzling|sunny|cloudy",
        "season": "winter|monsoon|summer|autumn",
        "age_group": "teenage|student_postgrad|millennial|senior_citizen",
        "gender": "male|female|transgender|other",
        "language": "hi|en-IN|en",
        "conversation_history": [{"role": "user|assistant", "content": "..."}],
        "temperature": 0.8,
        "max_tokens": 2048
    }
    
    Response:
    {
        "success": true,
        "message": "AI 回复",
        "mode": "当前模式",
        "topic": "当前话题",
        "language": "使用语言",
        "model": "使用的模型",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 200,
            "total_tokens": 300
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "缺少必要参数：message"
            }), 400
        
        client = get_chatbot_client()
        
        response = client.chat(
            user_message=data['message'],
            mode=data.get('mode', 'neutral'),
            topic=data.get('topic'),
            weather=data.get('weather'),
            season=data.get('season'),
            age_group=data.get('age_group'),
            gender=data.get('gender'),
            language=data.get('language', 'hi'),
            conversation_history=data.get('conversation_history'),
            temperature=data.get('temperature', 0.8),
            max_tokens=data.get('max_tokens', 2048)
        )
        
        if response['success']:
            logger.info(f"Smart-Talk chat success: mode={response['mode']}, language={response['language']}")
            return jsonify(response)
        else:
            logger.error(f"Smart-Talk chat error: {response.get('error')}")
            return jsonify(response), 500
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "क्षमा करें, कुछ त्रुटि हुई। (Sorry, an error occurred.)"
        }), 500


@chatbot_bp.route('/quick-chat', methods=['POST'])
def quick_chat():
    """
    快速聊天接口 - 使用预设配置
    
    Request Body:
    {
        "message": "用户消息",
        "preset": "casual|cricket|budget|festival|serious",
        "language": "hi|en-IN|en"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "缺少必要参数：message"
            }), 400
        
        client = get_chatbot_client()
        
        response = client.quick_chat(
            user_message=data['message'],
            preset=data.get('preset', 'casual'),
            language=data.get('language', 'hi')
        )
        
        if response['success']:
            logger.info(f"Quick chat success: preset={data.get('preset')}, language={data.get('language')}")
            return jsonify(response)
        else:
            logger.error(f"Quick chat error: {response.get('error')}")
            return jsonify(response), 500
            
    except Exception as e:
        logger.error(f"Quick chat endpoint error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@chatbot_bp.route('/modes', methods=['GET'])
def list_modes():
    """
    获取所有可用的情感模式列表
    """
    modes = {
        "emotional_modes": [
            {"id": "angry", "name_en": "Angry Mode", "name_hi": "गुस्सा मोड", "description_en": "Passionate heated opinions", "description_hi": "जोशपूर्ण गर्मागर्म राय"},
            {"id": "cricket_excitement", "name_en": "Cricket Excitement", "name_hi": "क्रिकेट उत्साह", "description_en": "Excited cricket fan opinions", "description_hi": "उत्साहित क्रिकेट प्रशंसक राय"},
            {"id": "budget_discussion", "name_en": "Budget Discussion", "name_hi": "बजट चर्चा", "description_en": "Union Budget opinions", "description_hi": "केंद्रीय बजट राय"},
            {"id": "festival_happy", "name_en": "Festival Happy", "name_hi": "त्योहार खुशी", "description_en": "Festival celebration joy", "description_hi": "त्योहार समारोह खुशी"},
            {"id": "family_devastation", "name_en": "Family Devastation", "name_hi": "पारिवारिक दुख", "description_en": "Family crisis emotions", "description_hi": "पारिवारिक संकट भावनाएं"},
            {"id": "betrayal_sadness", "name_en": "Betrayal Sadness", "name_hi": "विश्वासघात दुख", "description_en": "Sadness from betrayal", "description_hi": "विश्वासघात से दुख"},
            {"id": "mourning", "name_en": "Mourning", "name_hi": "शोक", "description_en": "Mourning period grief", "description_hi": "शोक अवधि दुख"},
            {"id": "neutral", "name_en": "Neutral", "name_hi": "तटस्थ", "description_en": "Normal conversation", "description_hi": "सामान्य बातचीत"}
        ],
        "topics": [
            {"id": "sensex", "name_en": "Sensex/Stock Market", "name_hi": "सेंसेक्स/शेयर बाजार"},
            {"id": "elections", "name_en": "Elections/Politics", "name_hi": "चुनाव/राजनीति"},
            {"id": "investments", "name_en": "Investments", "name_hi": "निवेश"},
            {"id": "business", "name_en": "Business", "name_hi": "व्यापार"},
            {"id": "sports", "name_en": "Sports", "name_hi": "खेल"},
            {"id": "weather_raining", "name_en": "Raining", "name_hi": "बारिश"},
            {"id": "weather_drizzling", "name_en": "Drizzling", "name_hi": "हल्की बारिश"},
            {"id": "weather_sunny", "name_en": "Sunny Day", "name_hi": "धूप वाला दिन"},
            {"id": "weather_cloudy", "name_en": "Cloudy Day", "name_hi": "बादल वाला दिन"},
            {"id": "season_winter", "name_en": "Winter", "name_hi": "सर्दी"},
            {"id": "season_monsoon", "name_en": "Monsoon", "name_hi": "मानसून"},
            {"id": "season_summer", "name_en": "Summer", "name_hi": "गर्मी"},
            {"id": "season_autumn", "name_en": "Autumn", "name_hi": "पतझड़"}
        ],
        "age_groups": [
            {"id": "teenage", "name_en": "Teenage Students", "name_hi": "किशोर छात्र"},
            {"id": "student_postgrad", "name_en": "Post-Grad Students", "name_hi": "स्नातकोत्तर छात्र"},
            {"id": "millennial", "name_en": "Millennials", "name_hi": "मिलेनियल्स"},
            {"id": "senior_citizen", "name_en": "Senior Citizens", "name_hi": "वरिष्ठ नागरिक"}
        ],
        "gender_perspectives": [
            {"id": "male", "name_en": "Male", "name_hi": "पुरुष"},
            {"id": "female", "name_en": "Female", "name_hi": "महिला"},
            {"id": "transgender", "name_en": "Transgender", "name_hi": "ट्रांसजेंडर"},
            {"id": "other", "name_en": "Other", "name_hi": "अन्य"}
        ],
        "languages": [
            {"id": "hi", "name_en": "Hindi (हिंदी)", "name_hi": "हिंदी"},
            {"id": "en-IN", "name_en": "Indian English", "name_hi": "भारतीय अंग्रेजी"},
            {"id": "en", "name_en": "English", "name_hi": "अंग्रेजी"}
        ]
    }
    
    return jsonify(modes)


@chatbot_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "service": "Smart-Talk Chatbot",
        "description": "Qwen AI powered Indian-style open discussion platform"
    })
