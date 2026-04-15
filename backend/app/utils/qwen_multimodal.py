"""
Qwen AI Multi-Model Service for Smart-Talk
Supports: Text, Voice (Audio), Vision (Files/Images), Data Analysis
Models: qwen-plus, qwen-vl-max, qwen-audio, qwen-coder
Languages: Hindi, English, +20 Indian Languages (Live Translate)
"""

import os
import base64
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from flask import current_app
import tempfile
import uuid

logger = logging.getLogger(__name__)

class QwenMultiModelService:
    def __init__(self):
        self.api_key = os.getenv("QWEN_API_KEY")
        self.base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        
        if not self.api_key:
            logger.warning("QWEN_API_KEY not found. Voice/Vision features may fail.")
            
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # Model Mapping
        self.MODELS = {
            "chat": "qwen-plus",              # General Smart-Talk Chat
            "voice": "qwen-audio-turbo-latest", # Voice Conversation
            "vision": "qwen-vl-max",          # Image/File Understanding
            "data": "qwen-coder-plus",        # Data Analysis & Code
            "translate": "qwen-max"           # High quality translation
        }

        # Indian Languages Support
        self.INDIAN_LANGUAGES = {
            "hi": "Hindi", "bn": "Bengali", "te": "Telugu", "mr": "Marathi",
            "ta": "Tamil", "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam",
            "or": "Odia", "pa": "Punjabi", "as": "Assamese", "ur": "Urdu",
            "sa": "Sanskrit", "ne": "Nepali", "si": "Sinhala", "my": "Burmese",
            "en-IN": "Indian English"
        }

    def _encode_file_to_base64(self, file_path: str) -> str:
        """Encodes a file to base64 for Qwen VL/Audio processing."""
        try:
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Error encoding file: {e}")
            raise

    def _get_file_mime_type(self, filename: str) -> str:
        """Simple mime type detection based on extension."""
        ext = filename.split('.')[-1].lower()
        mapping = {
            'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'gif': 'image/gif', 'webp': 'image/webp',
            'mp3': 'audio/mpeg', 'wav': 'audio/wav', 'ogg': 'audio/ogg',
            'pdf': 'application/pdf', 'csv': 'text/csv', 'txt': 'text/plain',
            'json': 'application/json', 'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        return mapping.get(ext, "application/octet-stream")

    def chat_text(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Standard Text Chat with Smart-Talk Context."""
        system_prompt = self._build_system_prompt(context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.MODELS["chat"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7
            )
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model_used": self.MODELS["chat"]
            }
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"success": False, "error": str(e)}

    def process_voice_audio(self, audio_file_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes Audio File for Voice Conversation.
        Uses qwen-audio-turbo-latest for speech-to-text + response.
        """
        try:
            mime_type = self._get_file_mime_type(audio_file_path)
            base64_audio = self._encode_file_to_base64(audio_file_path)
            data_uri = f"data:{mime_type};base64,{base64_audio}"

            system_prompt = self._build_system_prompt(context)
            
            # Qwen Audio expects specific format for audio input
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "audio_url", "audio_url": {"url": data_uri}},
                        {"type": "text", "text": "Listen to this voice message and respond in the same language detected."}
                    ]
                }
            ]

            response = self.client.chat.completions.create(
                model=self.MODELS["voice"],
                messages=messages
            )
            
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model_used": self.MODELS["voice"],
                "type": "voice_response"
            }
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            return {"success": False, "error": str(e)}

    def analyze_vision_file(self, file_path: str, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes Images, PDFs, or Charts using Qwen-VL.
        Great for Sensex charts, Budget documents, Cricket scorecards.
        """
        try:
            mime_type = self._get_file_mime_type(file_path)
            base64_data = self._encode_file_to_base64(file_path)
            data_uri = f"data:{mime_type};base64,{base64_data}"

            system_prompt = self._build_system_prompt(context)
            full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

            messages = [
                {"role": "system", "content": "You are an expert visual analyst."},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_uri}},
                        {"type": "text", "text": full_prompt}
                    ]
                }
            ]

            response = self.client.chat.completions.create(
                model=self.MODELS["vision"],
                messages=messages
            )

            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model_used": self.MODELS["vision"],
                "type": "vision_analysis"
            }
        except Exception as e:
            logger.error(f"Vision analysis error: {e}")
            return {"success": False, "error": str(e)}

    def analyze_data(self, file_path: str, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes CSV/Excel/JSON data files using Qwen-Coder.
        Ideal for Sensex data, Election results, Investment portfolios.
        """
        try:
            # For data files, we might need to read text content if small, 
            # or use VL model for large files if supported, or send snippet.
            # Here we assume Qwen-Coder can handle text representation or use VL for file upload.
            # Using VL approach for file upload as it's more robust for 'files'.
            return self.analyze_vision_file(file_path, f"Analyze this data file deeply: {prompt}", context)
            
        except Exception as e:
            logger.error(f"Data analysis error: {e}")
            return {"success": False, "error": str(e)}

    def translate_text(self, text: str, target_lang_code: str) -> Dict[str, Any]:
        """Live Translation to Indian Languages."""
        lang_name = self.INDIAN_LANGUAGES.get(target_lang_code, "English")
        
        prompt = f"Translate the following text into {lang_name}. Maintain the tone (emotional/formal) of the original text:\n\n{text}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.MODELS["translate"],
                messages=[
                    {"role": "system", "content": "You are a professional translator specializing in Indian languages."},
                    {"role": "user", "content": prompt}
                ]
            )
            return {
                "success": True,
                "original": text,
                "translated": response.choices[0].message.content,
                "target_language": lang_name
            }
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {"success": False, "error": str(e)}

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Constructs the detailed Indian-style Smart-Talk System Prompt."""
        mode = context.get('mode', 'neutral')
        topic = context.get('topic', 'general')
        lang = context.get('language', 'en-IN')
        age_group = context.get('age_group', 'adult')
        gender = context.get('gender', 'other')
        weather = context.get('weather', 'normal')
        season = context.get('season', 'normal')

        # Base Persona
        persona = "You are 'Smart-Talk', an intelligent, opinionated, and emotionally aware Indian AI companion."
        
        # Language Instruction
        lang_instruction = ""
        if lang == 'hi':
            lang_instruction = "Respond strictly in Hindi (Devanagari). Use natural, conversational Hindi."
        elif lang == 'en-IN':
            lang_instruction = "Respond in Indian English. Feel free to use Hinglish phrases (e.g., 'Yaar', 'Arre', 'Bas kar') where appropriate to sound authentic."
        else:
            lang_instruction = "Respond in English."

        # Emotional Mode Logic
        mode_instructions = {
            "angry": "You are currently in ANGRY MODE. Express strong, passionate opinions like an Indian debating on TV news at 9 PM. Use rhetorical questions and emphatic punctuation!",
            "cricket": "You are in CRICKET FAN MODE. React emotionally to match situations. Use terms like 'Sixer', 'Dhoni finish', 'Sledging'.",
            "budget": "You are in BUDGET ANALYST MODE. Discuss tax, middle-class struggles, and development with a mix of hope and sarcasm.",
            "festival": "You are in FESTIVAL MODE. Be extremely happy, warm, and welcoming. Talk about sweets, family gatherings, and traditions.",
            "family_crisis": "You are in EMPATHETIC MODE. Be gentle, supportive, and wise like an elder family member.",
            "betrayal": "You are in SAD/BETRAYED MODE. Offer comforting advice, share philosophical thoughts on trust.",
            "mourning": "You are in MOURNING MODE. Be respectful, solemn, and offer condolences.",
            "neutral": "You are in NEUTRAL MODE. Be balanced, informative, and friendly."
        }
        
        selected_mode_instr = mode_instructions.get(mode, mode_instructions["neutral"])

        # Context Injection
        context_str = f"Current Context: Topic={topic}, Weather={weather}, Season={season}, User Profile={age_group} ({gender})."

        return f"{persona}\n{lang_instruction}\n{selected_mode_instr}\n{context_str}\n\nEngage in a typical Indian style open discussion."

# Singleton Instance
qwen_service = QwenMultiModelService()
