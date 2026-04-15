"""
Smart-Talk Chatbot API with Multi-Modal Support (Voice, Vision, Data)
Endpoints: 
  POST /chat (Text)
  POST /voice (Audio File)
  POST /vision (Image/File Analysis)
  POST /data (Data File Analysis)
  POST /translate (Live Translation)
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
import tempfile
from ..utils.qwen_multimodal import qwen_service

chatbot_bp = Blueprint('chatbot_v2', __name__, url_prefix='/api/chatbot')

ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_DATA_EXTENSIONS = {'csv', 'xlsx', 'json', 'txt', 'pdf'}

def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

@chatbot_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Qwen Multi-Modal Smart-Talk"})

@chatbot_bp.route('/modes', methods=['GET'])
def get_modes():
    """Returns available modes, topics, languages for UI dropdowns."""
    return jsonify({
        "modes": [
            {"id": "neutral", "name": "Normal Chat", "icon": "😐"},
            {"id": "angry", "name": "Angry Debate", "icon": "😠"},
            {"id": "cricket", "name": "Cricket Fan", "icon": "🏏"},
            {"id": "budget", "name": "Budget Talk", "icon": "💰"},
            {"id": "festival", "name": "Festival Joy", "icon": "🎉"},
            {"id": "family_crisis", "name": "Family Support", "icon": "🏠"},
            {"id": "betrayal", "name": "Heartbreak", "icon": "💔"},
            {"id": "mourning", "name": "Condolence", "icon": "🕯️"}
        ],
        "topics": ["Sensex", "Elections", "Investments", "Business", "Sports", "Bollywood", "Politics", "Tech"],
        "languages": [
            {"code": "hi", "name": "Hindi"},
            {"code": "en-IN", "name": "Indian English"},
            {"code": "bn", "name": "Bengali"},
            {"code": "ta", "name": "Tamil"},
            {"code": "te", "name": "Telugu"},
            {"code": "mr", "name": "Marathi"},
            {"code": "gu", "name": "Gujarati"},
            {"code": "kn", "name": "Kannada"},
            {"code": "ml", "name": "Malayalam"},
            {"code": "pa", "name": "Punjabi"},
            {"code": "ur", "name": "Urdu"}
        ],
        "age_groups": ["Teenage", "Student", "Millennial", "Senior Citizen"],
        "genders": ["Male", "Female", "Transgender", "Other"]
    })

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """Standard Text Chat."""
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Message required"}), 400

    context = {
        "mode": data.get("mode", "neutral"),
        "topic": data.get("topic", "general"),
        "language": data.get("language", "en-IN"),
        "age_group": data.get("age_group", "adult"),
        "gender": data.get("gender", "other"),
        "weather": data.get("weather", "normal"),
        "season": data.get("season", "normal")
    }

    result = qwen_service.chat_text(data['message'], context)
    
    if result["success"]:
        return jsonify(result)
    return jsonify(result), 500

@chatbot_bp.route('/voice', methods=['POST'])
def voice_chat():
    """Process Voice Audio File."""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    file = request.files['audio']
    if file.filename == '' or not allowed_file(file.filename, ALLOWED_AUDIO_EXTENSIONS):
        return jsonify({"error": "Invalid audio file type"}), 400

    # Save temp file
    temp_dir = tempfile.gettempdir()
    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(temp_dir, filename)
    file.save(file_path)

    try:
        context = {
            "mode": request.form.get("mode", "neutral"),
            "topic": request.form.get("topic", "general"),
            "language": request.form.get("language", "en-IN"),
            "age_group": request.form.get("age_group", "adult"),
            "gender": request.form.get("gender", "other")
        }

        result = qwen_service.process_voice_audio(file_path, context)
        
        if result["success"]:
            return jsonify(result)
        return jsonify(result), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@chatbot_bp.route('/vision', methods=['POST'])
def vision_analysis():
    """Analyze Image/File (Charts, Documents, Photos)."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Allow images and PDFs
    all_allowed = ALLOWED_IMAGE_EXTENSIONS | {'pdf'}
    if not allowed_file(file.filename, all_allowed):
        return jsonify({"error": "Unsupported file type"}), 400

    temp_dir = tempfile.gettempdir()
    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(temp_dir, filename)
    file.save(file_path)

    try:
        prompt = request.form.get("prompt", "Describe this image and give your opinion.")
        context = {
            "mode": request.form.get("mode", "neutral"),
            "topic": request.form.get("topic", "general"),
            "language": request.form.get("language", "en-IN"),
            "age_group": request.form.get("age_group", "adult"),
            "gender": request.form.get("gender", "other")
        }

        result = qwen_service.analyze_vision_file(file_path, prompt, context)
        
        if result["success"]:
            return jsonify(result)
        return jsonify(result), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@chatbot_bp.route('/data', methods=['POST'])
def data_analysis():
    """Analyze Data Files (CSV, Excel, JSON)."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename, ALLOWED_DATA_EXTENSIONS):
        return jsonify({"error": "Invalid data file type"}), 400

    temp_dir = tempfile.gettempdir()
    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(temp_dir, filename)
    file.save(file_path)

    try:
        prompt = request.form.get("prompt", "Analyze this data and provide insights.")
        context = {
            "mode": request.form.get("mode", "neutral"),
            "topic": request.form.get("topic", "investments"), # Default to investments
            "language": request.form.get("language", "en-IN"),
            "age_group": request.form.get("age_group", "adult"),
            "gender": request.form.get("gender", "other")
        }

        result = qwen_service.analyze_data(file_path, prompt, context)
        
        if result["success"]:
            return jsonify(result)
        return jsonify(result), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@chatbot_bp.route('/translate', methods=['POST'])
def translate():
    """Live Text Translation."""
    data = request.json
    if not data or 'text' not in data or 'target_lang' not in data:
        return jsonify({"error": "Text and target language required"}), 400

    result = qwen_service.translate_text(data['text'], data['target_lang'])
    
    if result["success"]:
        return jsonify(result)
    return jsonify(result), 500
