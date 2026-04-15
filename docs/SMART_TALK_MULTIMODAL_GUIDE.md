# 🇮🇳 Smart-Talk Multi-Modal Chatbot Integration Guide

## Overview
This guide details the integration of **Qwen AI Multi-Model** capabilities into the MiroFish Smart-Talk platform, enabling:
- 💬 **Text Chat** (Emotional Modes)
- 🎤 **Voice Conversation** (Live Talk)
- 📷 **Vision Analysis** (Image/File Understanding)
- 📊 **Data Analysis** (CSV/Excel/JSON)
- 🌐 **Live Translation** (20+ Indian Languages)

---

## 🏗️ Architecture

### Backend Stack
- **Framework**: Flask (Python)
- **AI Client**: OpenAI-compatible API for Qwen Models
- **Models Used**:
  - `qwen-plus`: General Smart-Talk Chat
  - `qwen-audio-turbo-latest`: Voice Conversation
  - `qwen-vl-max`: Vision (Images, PDFs)
  - `qwen-coder-plus`: Data Analysis
  - `qwen-max`: High-quality Translation

### Frontend Stack
- **Framework**: Vue.js 3
- **Component**: `SmartTalkMultimodal.vue` (Right Side Panel)
- **Features**: Voice Recording, File Upload, Real-time Translation

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `backend/app/utils/qwen_multimodal.py` | Core AI service (Text, Voice, Vision, Data, Translate) |
| `backend/app/api/chatbot_v2.py` | REST API endpoints |
| `frontend/src/api/chatbot-multimodal.js` | JavaScript API client |
| `frontend/src/components/SmartTalkMultimodal.vue` | UI Side Panel Component |

---

## ⚙️ Configuration

### 1. Environment Variables
Add to your `.env` file:

```bash
# Qwen AI Configuration
QWEN_API_KEY=your_dashscope_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL_NAME=qwen-plus
```

> **Get API Key**: Visit [Alibaba Cloud DashScope](https://dashscope.console.aliyun.com/)

### 2. Install Dependencies

**Backend:**
```bash
cd backend
pip install openai flask werkzeug
```

**Frontend:**
```bash
cd frontend
npm install axios
```

### 3. Register Blueprint

In `backend/app/__init__.py`:
```python
from .api.chatbot_v2 import chatbot_bp

def create_app():
    app = Flask(__name__)
    # ... other blueprints
    app.register_blueprint(chatbot_bp)
    return app
```

---

## 🚀 API Endpoints

### 1. Get Configuration
```http
GET /api/chatbot/modes
```
**Response:**
```json
{
  "modes": [{"id": "cricket", "name": "Cricket Fan", "icon": "🏏"}],
  "topics": ["Sensex", "Elections", "Sports"],
  "languages": [{"code": "hi", "name": "Hindi"}]
}
```

### 2. Text Chat
```http
POST /api/chatbot/chat
Content-Type: application/json

{
  "message": "क्रिकेट मैच कैसा रहा?",
  "mode": "cricket",
  "language": "hi",
  "topic": "Sports"
}
```

### 3. Voice Chat
```http
POST /api/chatbot/voice
Content-Type: multipart/form-data

Form Data:
- audio: [audio_file.webm]
- mode: "angry"
- language: "hi"
```

### 4. Vision Analysis (Image/File)
```http
POST /api/chatbot/vision
Content-Type: multipart/form-data

Form Data:
- file: [image.jpg]
- prompt: "Analyze this Sensex chart"
- topic: "Sensex"
```

### 5. Data Analysis (CSV/Excel)
```http
POST /api/chatbot/data
Content-Type: multipart/form-data

Form Data:
- file: [portfolio.xlsx]
- prompt: "Give investment advice"
- topic: "Investments"
```

### 6. Live Translation
```http
POST /api/chatbot/translate
Content-Type: application/json

{
  "text": "Happy Diwali!",
  "target_lang": "hi"
}
```

---

## 🎨 Frontend Usage

### Import Component
In your main Vue app (e.g., `App.vue`):

```vue
<template>
  <div id="app">
    <!-- Your existing content -->
    
    <!-- Smart-Talk Side Panel -->
    <SmartTalkMultimodal />
  </div>
</template>

<script>
import SmartTalkMultimodal from '@/components/SmartTalkMultimodal.vue';

export default {
  components: { SmartTalkMultimodal }
};
</script>
```

### Features Available in UI
- **Toggle Panel**: Click Indian flag button on right edge
- **Settings Gear**: Change Mode, Topic, Language, Age, Gender
- **Quick Actions**: One-click Cricket, Budget, Festival, Angry modes
- **Voice Button**: 🎤 Hold to record, release to send
- **File Upload**: 📎 Attach images, PDFs, Excel files
- **Translate Button**: 🌐 Convert AI response to selected language

---

## 🇮🇳 Supported Indian Languages

| Code | Language | Script |
|------|----------|--------|
| `hi` | Hindi | Devanagari |
| `bn` | Bengali | Bengali |
| `te` | Telugu | Telugu |
| `mr` | Marathi | Devanagari |
| `ta` | Tamil | Tamil |
| `gu` | Gujarati | Gujarati |
| `kn` | Kannada | Kannada |
| `ml` | Malayalam | Malayalam |
| `pa` | Punjabi | Gurmukhi |
| `ur` | Urdu | Perso-Arabic |
| `en-IN` | Indian English | Latin |

---

## 🎭 Emotional Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| 😠 **Angry** | Passionate debate style | Political arguments |
| 🏏 **Cricket** | Emotional fan reactions | Match discussions |
| 💰 **Budget** | Tax & middle-class focus | Union Budget talk |
| 🎉 **Festival** | Happy, warm, traditional | Diwali, Holi, Eid |
| 🏠 **Family Crisis** | Empathetic, wise elder | Personal problems |
| 💔 **Betrayal** | Comforting, philosophical | Relationship issues |
| 🕯️ **Mourning** | Respectful, solemn | Condolences |
| 😐 **Neutral** | Balanced, informative | General chat |

---

## 🧪 Testing

### Test Text Chat (Hindi)
```bash
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "आज का क्रिकेट मैच देखा?",
    "mode": "cricket",
    "language": "hi"
  }'
```

### Test Voice (Requires Audio File)
```bash
curl -X POST http://localhost:5000/api/chatbot/voice \
  -F "audio=@test_voice.webm" \
  -F "mode=festival" \
  -F "language=hi"
```

### Test Vision (Sensex Chart)
```bash
curl -X POST http://localhost:5000/api/chatbot/vision \
  -F "file=@sensex_chart.png" \
  -F "prompt=Is market bullish or bearish?" \
  -F "topic=Sensex"
```

---

## 🔒 Security Considerations

1. **API Key Protection**: Never commit `.env` to Git
2. **File Upload Limits**: Implement size limits in production
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Input Sanitization**: Validate all user inputs
5. **CORS**: Configure CORS for frontend domain only

---

## 🛠️ Troubleshooting

### Issue: "QWEN_API_KEY not found"
**Solution**: Ensure `.env` file exists and contains valid key.

### Issue: Microphone not working
**Solution**: Check browser permissions and HTTPS requirement.

### Issue: File upload fails
**Solution**: Verify file type is in allowed extensions list.

### Issue: Hindi text displays as squares
**Solution**: Ensure font supports Devanagari script (use Noto Sans Hindi).

---

## 📈 Future Enhancements

- [ ] **Text-to-Speech**: Play AI responses as audio in Indian voices
- [ ] **Video Analysis**: Support short video clips for cricket highlights
- [ ] **Group Chat**: Multi-user discussion rooms
- [ ] **Sentiment Analysis**: Detect user mood automatically
- [ ] **Offline Mode**: Cache common responses for low connectivity

---

## 🙏 Conclusion

The Smart-Talk Multi-Modal Chatbot brings a truly **Indian-style open discussion** experience to MiroFish, combining cutting-edge Qwen AI models with cultural context, emotional intelligence, and multilingual support.

**जय हिंद! वन्दे मातरम्!** 🇮🇳

---

*Created for MiroFish Project - Smart-Talk Initiative*
