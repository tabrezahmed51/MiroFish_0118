# Smart-Talk Chatbot Integration Guide
## Qwen AI Powered Indian-Style Open Discussion Platform

---

## 🎯 Overview (अवलोकन)

**Smart-Talk** is an innovative chatbot feature that enables Indian-style open discussions using Qwen AI models. It supports multiple emotional modes, topics, weather/season contexts, age groups, gender perspectives, and languages (Hindi, English, Indian English).

**स्मार्ट-टॉक** एक अभिनव चैटबॉट सुविधा है जो क्वेन एआई मॉडल का उपयोग करके भारतीय शैली की खुली चर्चा को सक्षम बनाती है।

---

## 🚀 Features (विशेषताएं)

### 1. Emotional Modes (भावनात्मक मोड्स)
- **Angry Mode** - Passionate heated opinions like Indian debates
- **Cricket Excitement** - Emotional cricket fan reactions
- **Budget Discussion** - Union Budget opinions with middle-class perspective
- **Festival Happy** - Joy of celebrating Diwali, Holi, Eid, Christmas
- **Family Devastation** - Deep emotions during family crises
- **Betrayal Sadness** - Sadness from broken relationships
- **Mourning** - Respectful grief expression
- **Neutral** - Normal conversation

### 2. Topics (विषय)
- Sensex/Stock Market
- Elections/Politics
- Investments
- Business/Startups
- Sports (Cricket, Hockey, Football)
- Weather contexts (Raining, Drizzling, Sunny, Cloudy)
- Seasons (Winter, Monsoon, Summer, Autumn)

### 3. Demographics (जनसांख्यिकी)
- **Age Groups**: Teenage, Post-Grad Students, Millennials, Senior Citizens
- **Gender Perspectives**: Male, Female, Transgender, Other
- **Languages**: Hindi (हिंदी), Indian English, English

---

## 📁 Files Created/Modified

### Backend Files
```
backend/
├── app/
│   ├── utils/
│   │   └── qwen_chatbot.py          # NEW: Qwen AI client for Smart-Talk
│   ├── api/
│   │   └── chatbot.py               # NEW: Chatbot API routes
│   ├── __init__.py                  # MODIFIED: Added chatbot blueprint
│   └── config.py                    # MODIFIED: Added Qwen configuration
└── .env.qwen.example                # NEW: Example environment file
```

### Frontend Files
```
frontend/
└── src/
    ├── api/
    │   └── chatbot.js               # NEW: Chatbot API client
    └── components/
        └── SmartTalkChatbot.vue     # NEW: Vue component
```

---

## ⚙️ Configuration

### 1. Environment Variables

Add to your `.env` file or create from `.env.qwen.example`:

```bash
# Qwen AI Configuration
QWEN_API_KEY=your_qwen_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL_NAME=qwen-plus
```

### 2. Qwen Model Options

| Model | Description | Use Case |
|-------|-------------|----------|
| `qwen-turbo` | Fast & cost-effective | Quick responses |
| `qwen-plus` | Balanced (default) | General use |
| `qwen-max` | Maximum capability | Complex discussions |
| `qwen-long` | Extended context | Long conversations |

### 3. Fallback Configuration

If `QWEN_API_KEY` is not set, the system will fallback to `LLM_API_KEY`.

---

## 🔌 API Endpoints

### 1. POST `/api/chatbot/chat`

Full chat with all Smart-Talk options.

**Request Body:**
```json
{
  "message": "क्रिकेट मैच के बारे में क्या सोचते हैं?",
  "mode": "cricket_excitement",
  "topic": "sports",
  "weather": "raining",
  "season": "monsoon",
  "age_group": "millennial",
  "gender": "male",
  "language": "hi",
  "conversation_history": [
    {"role": "user", "content": "पिछला मैच देखा?"},
    {"role": "assistant", "content": "हाँ, बहुत रोमांचक था!"}
  ],
  "temperature": 0.8,
  "max_tokens": 2048
}
```

**Response:**
```json
{
  "success": true,
  "message": "अरे यार! क्या मैच था! विराट ने तो कमाल कर दिया...",
  "mode": "cricket_excitement",
  "topic": "sports",
  "language": "hi",
  "model": "qwen-plus",
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350
  }
}
```

### 2. POST `/api/chatbot/quick-chat`

Quick chat with preset configurations.

**Request Body:**
```json
{
  "message": "आज का मैच कैसा रहा?",
  "preset": "cricket",
  "language": "hi"
}
```

**Presets Available:**
- `casual` - Normal conversation
- `cricket` - Cricket discussion
- `budget` - Budget discussion
- `festival` - Festival celebration
- `serious` - Serious topics (Sensex, etc.)

### 3. GET `/api/chatbot/modes`

Get all available modes and configurations.

**Response:**
```json
{
  "emotional_modes": [...],
  "topics": [...],
  "age_groups": [...],
  "gender_perspectives": [...],
  "languages": [...]
}
```

### 4. GET `/api/chatbot/health`

Health check endpoint.

---

## 💻 Frontend Usage

### Using the Component

```vue
<template>
  <div>
    <SmartTalkChatbot />
  </div>
</template>

<script>
import SmartTalkChatbot from '@/components/SmartTalkChatbot.vue';

export default {
  components: { SmartTalkChatbot }
};
</script>
```

### Using the API Client

```javascript
import { chatbotAPI, EMOTIONAL_MODES, LANGUAGES } from '@/api/chatbot';

// Full chat
const response = await chatbotAPI.chat({
  message: 'बजट पर आपकी राय?',
  mode: EMOTIONAL_MODES.BUDGET_DISCUSSION,
  topic: 'elections',
  language: LANGUAGES.HINDI
});

// Quick chat
const quickResponse = await chatbotAPI.quickChat(
  'क्रिकेट मैच कैसा था?',
  'cricket',
  'hi'
);

// Get available modes
const modes = await chatbotAPI.getModes();
```

---

## 🎨 UI Features

The Smart-Talk Chatbot component includes:

1. **Tricolor Theme** - Indian flag colors (Saffron, White, Green)
2. **Settings Panel** - Configure mode, topic, age group, language
3. **Quick Actions** - One-click presets for Cricket, Budget, Festival, Casual
4. **Bilingual Support** - Hindi and English throughout the UI
5. **Typing Indicator** - Animated dots while waiting for response
6. **Message Metadata** - Shows mode and language tags
7. **Responsive Design** - Works on desktop and mobile

---

## 🧪 Testing

### Test with cURL

```bash
# Test health check
curl http://localhost:5000/api/chatbot/health

# Get available modes
curl http://localhost:5000/api/chatbot/modes

# Send a chat message
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "नमस्ते! कैसे हैं?",
    "mode": "neutral",
    "language": "hi"
  }'

# Quick chat
curl -X POST http://localhost:5000/api/chatbot/quick-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "क्रिकेट मैच कैसा था?",
    "preset": "cricket",
    "language": "hi"
  }'
```

### Test in Browser

1. Start backend: `cd backend && python run.py`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to the page with `<SmartTalkChatbot />` component
4. Try different modes and languages

---

## 🔒 Security & Ethics

### Guidelines Implemented

1. **Cultural Sensitivity** - Respects Indian diversity (religion, caste, region, language)
2. **Inclusivity** - Supports all gender identities
3. **No Stereotypes** - Embraces cultural richness without generalizations
4. **Respectful Discourse** - Passionate but respectful opinions
5. **Age-Appropriate** - Different perspectives for different age groups

### Content Moderation

The system is designed to:
- Avoid controversial political statements
- Not promote hate speech or discrimination
- Maintain respectful tone even in "Angry Mode"
- Provide balanced perspectives

---

## 🚀 Future Enhancements

### Planned Features

1. **Voice Input/Output** - Hindi voice recognition and synthesis
2. **Regional Languages** - Tamil, Telugu, Bengali, Marathi, etc.
3. **Sentiment Analysis** - Track user mood over time
4. **Personalization** - Remember user preferences
5. **Group Discussions** - Multi-user Smart-Talk sessions
6. **Social Sharing** - Share interesting opinions on social media
7. **Opinion Polls** - Create and participate in polls
8. **Trending Topics** - Real-time trending discussions

### Technical Improvements

1. **Caching** - Cache common responses for faster replies
2. **Rate Limiting** - Prevent API abuse
3. **Analytics** - Track usage patterns
4. **A/B Testing** - Test different prompts and modes
5. **Multi-Model Support** - Switch between Qwen models dynamically

---

## 📞 Support

For issues or questions:
- Check logs in `backend/logs/`
- Review API responses for error messages
- Ensure Qwen API key is valid
- Verify network connectivity to Qwen endpoints

---

## 🙏 Credits

**Smart-Talk** - Made with ❤️ for India

Powered by:
- Qwen AI Models (Alibaba Cloud)
- Flask Backend
- Vue.js Frontend
- Indian Cultural Context

---

## 📄 License

Same as main MiroFish project license.

---

**जय हिंद! वन्दे मातरम्!** 🇮🇳
