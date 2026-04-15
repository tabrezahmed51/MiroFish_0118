<template>
  <div class="smart-talk-chatbot">
    <!-- Header -->
    <div class="chatbot-header">
      <h3>🗣️ Smart-Talk (स्मार्ट-टॉक)</h3>
      <p class="subtitle">Indian Style Open Discussion | भारतीय शैली खुली चर्चा</p>
      <button @click="toggleSettings" class="settings-btn">⚙️</button>
    </div>

    <!-- Settings Panel -->
    <div v-if="showSettings" class="settings-panel">
      <div class="setting-group">
        <label>😌 Emotional Mode / भावनात्मक मोड:</label>
        <select v-model="selectedMode" class="setting-select">
          <option value="neutral">Neutral / तटस्थ</option>
          <option value="angry">Angry / गुस्सा</option>
          <option value="cricket_excitement">Cricket Excitement / क्रिकेट उत्साह</option>
          <option value="budget_discussion">Budget Discussion / बजट चर्चा</option>
          <option value="festival_happy">Festival Happy / त्योहार खुशी</option>
          <option value="family_devastation">Family Devastation / पारिवारिक दुख</option>
          <option value="betrayal_sadness">Betrayal Sadness / विश्वासघात दुख</option>
          <option value="mourning">Mourning / शोक</option>
        </select>
      </div>

      <div class="setting-group">
        <label>📝 Topic / विषय:</label>
        <select v-model="selectedTopic" class="setting-select">
          <option value="">Select Topic / विषय चुनें</option>
          <option value="sensex">Sensex / शेयर बाजार</option>
          <option value="elections">Elections / चुनाव</option>
          <option value="investments">Investments / निवेश</option>
          <option value="business">Business / व्यापार</option>
          <option value="sports">Sports / खेल</option>
        </select>
      </div>

      <div class="setting-group">
        <label>👤 Age Group / आयु वर्ग:</label>
        <select v-model="selectedAgeGroup" class="setting-select">
          <option value="">Any / कोई भी</option>
          <option value="teenage">Teenage / किशोर</option>
          <option value="student_postgrad">Post-Grad Student / स्नातकोत्तर छात्र</option>
          <option value="millennial">Millennial / मिलेनियल</option>
          <option value="senior_citizen">Senior Citizen / वरिष्ठ नागरिक</option>
        </select>
      </div>

      <div class="setting-group">
        <label>🌐 Language / भाषा:</label>
        <select v-model="selectedLanguage" class="setting-select">
          <option value="hi">हिंदी (Hindi)</option>
          <option value="en-IN">Indian English</option>
          <option value="en">English</option>
        </select>
      </div>
    </div>

    <!-- Chat Messages -->
    <div class="chat-messages" ref="messagesContainer">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', message.role]"
      >
        <div class="message-avatar">
          {{ message.role === 'user' ? '👤' : '🤖' }}
        </div>
        <div class="message-content">
          <div class="message-text">{{ message.content }}</div>
          <div v-if="message.mode" class="message-meta">
            <span class="mode-tag">{{ getModeName(message.mode) }}</span>
            <span v-if="message.language" class="language-tag">{{ message.language }}</span>
          </div>
        </div>
      </div>

      <div v-if="isLoading" class="message assistant loading">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <button @click="usePreset('cricket')" class="quick-btn">🏏 Cricket</button>
      <button @click="usePreset('budget')" class="quick-btn">💰 Budget</button>
      <button @click="usePreset('festival')" class="quick-btn">🎉 Festival</button>
      <button @click="usePreset('casual')" class="quick-btn">😊 Casual</button>
    </div>

    <!-- Input Area -->
    <div class="chat-input-area">
      <textarea
        v-model="userInput"
        @keydown.enter.exact.prevent="sendMessage"
        placeholder="अपनी राय लिखें... Share your opinion..."
        rows="2"
        class="chat-input"
      ></textarea>
      <button 
        @click="sendMessage" 
        :disabled="!userInput.trim() || isLoading"
        class="send-btn"
      >
        📤
      </button>
    </div>
  </div>
</template>

<script>
import { chatbotAPI, EMOTIONAL_MODES, LANGUAGES } from '@/api/chatbot';

export default {
  name: 'SmartTalkChatbot',
  
  data() {
    return {
      messages: [],
      userInput: '',
      isLoading: false,
      showSettings: false,
      selectedMode: 'neutral',
      selectedTopic: '',
      selectedAgeGroup: '',
      selectedLanguage: 'hi',
      conversationHistory: []
    };
  },

  mounted() {
    // Welcome message
    this.addMessage({
      role: 'assistant',
      content: 'नमस्ते! Welcome to Smart-Talk! 🙏\n\nमैं आपकी राय जानना चाहता हूँ। किस विषय पर बात करें?\n(I want to know your opinion. What shall we discuss?)',
      language: 'hi'
    });
  },

  methods: {
    toggleSettings() {
      this.showSettings = !this.showSettings;
    },

    usePreset(preset) {
      const presets = {
        cricket: 'क्रिकेट मैच के बारे में क्या सोचते हैं? आज का मैच कैसा रहा?',
        budget: 'इस बार के बजट पर आपकी क्या राय है? मध्यम वर्ग को क्या लाभ मिला?',
        festival: 'आपका पसंदीदा त्योहार कौन सा है और क्यों?',
        casual: 'नमस्ते! कैसे हैं आप?'
      };
      
      this.userInput = presets[preset] || presets.casual;
      
      // Set appropriate mode
      const modeMap = {
        cricket: 'cricket_excitement',
        budget: 'budget_discussion',
        festival: 'festival_happy',
        casual: 'neutral'
      };
      this.selectedMode = modeMap[preset] || 'neutral';
    },

    async sendMessage() {
      if (!this.userInput.trim() || this.isLoading) return;

      const userMessage = this.userInput.trim();
      this.userInput = '';

      // Add user message to chat
      this.addMessage({
        role: 'user',
        content: userMessage
      });

      // Add to conversation history
      this.conversationHistory.push({
        role: 'user',
        content: userMessage
      });

      this.isLoading = true;

      try {
        const response = await chatbotAPI.chat({
          message: userMessage,
          mode: this.selectedMode,
          topic: this.selectedTopic || undefined,
          age_group: this.selectedAgeGroup || undefined,
          language: this.selectedLanguage,
          conversation_history: this.conversationHistory
        });

        if (response.success) {
          this.addMessage({
            role: 'assistant',
            content: response.message,
            mode: response.mode,
            language: response.language
          });

          // Add to conversation history
          this.conversationHistory.push({
            role: 'assistant',
            content: response.message
          });
        } else {
          this.addMessage({
            role: 'assistant',
            content: 'क्षमा करें, कुछ त्रुटि हुई। कृपया पुनः प्रयास करें।\n(Sorry, an error occurred. Please try again.)'
          });
        }
      } catch (error) {
        console.error('Chat error:', error);
        this.addMessage({
          role: 'assistant',
          content: `Error: ${error.message}`
        });
      } finally {
        this.isLoading = false;
        this.scrollToBottom();
      }
    },

    addMessage(message) {
      this.messages.push(message);
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },

    scrollToBottom() {
      const container = this.$refs.messagesContainer;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },

    getModeName(modeId) {
      const modeNames = {
        angry: 'गुस्सा (Angry)',
        cricket_excitement: 'क्रिकेट उत्साह',
        budget_discussion: 'बजट चर्चा',
        festival_happy: 'त्योहार खुशी',
        family_devastation: 'पारिवारिक दुख',
        betrayal_sadness: 'विश्वासघात दुख',
        mourning: 'शोक',
        neutral: 'तटस्थ'
      };
      return modeNames[modeId] || modeId;
    }
  }
};
</script>

<style scoped>
.smart-talk-chatbot {
  display: flex;
  flex-direction: column;
  height: 600px;
  background: linear-gradient(135deg, #ff9933 0%, #ffffff 50%, #138808 100%);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.chatbot-header {
  background: linear-gradient(90deg, #ff9933, #ffffff, #138808);
  padding: 15px 20px;
  text-align: center;
  position: relative;
}

.chatbot-header h3 {
  margin: 0;
  color: #000080;
  font-size: 1.5em;
  font-weight: bold;
}

.subtitle {
  margin: 5px 0 0;
  font-size: 0.9em;
  color: #333;
}

.settings-btn {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  font-size: 1.2em;
  transition: transform 0.2s;
}

.settings-btn:hover {
  transform: translateY(-50%) rotate(90deg);
}

.settings-panel {
  background: #f8f9fa;
  padding: 15px;
  border-bottom: 2px solid #ddd;
}

.setting-group {
  margin-bottom: 10px;
}

.setting-group:last-child {
  margin-bottom: 0;
}

.setting-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
  font-size: 0.9em;
}

.setting-select {
  width: 100%;
  padding: 8px 12px;
  border: 2px solid #ff9933;
  border-radius: 6px;
  font-size: 0.9em;
  background: white;
  cursor: pointer;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: rgba(255, 255, 255, 0.95);
}

.message {
  display: flex;
  margin-bottom: 15px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-avatar {
  font-size: 2em;
  margin: 0 10px;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message.user .message-content {
  background: linear-gradient(135deg, #ff9933, #ff6600);
  color: white;
}

.message.assistant .message-content {
  background: white;
  color: #333;
}

.message-text {
  line-height: 1.5;
  white-space: pre-wrap;
}

.message-meta {
  margin-top: 8px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.mode-tag,
.language-tag {
  font-size: 0.75em;
  padding: 3px 8px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.1);
}

.typing-indicator {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #ff9933;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.quick-actions {
  display: flex;
  gap: 8px;
  padding: 10px 20px;
  background: #f8f9fa;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 8px 16px;
  border: 2px solid #ff9933;
  background: white;
  color: #ff9933;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #ff9933;
  color: white;
  transform: translateY(-2px);
}

.chat-input-area {
  display: flex;
  gap: 10px;
  padding: 15px 20px;
  background: white;
  border-top: 2px solid #eee;
}

.chat-input {
  flex: 1;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  resize: none;
  font-family: inherit;
  font-size: 0.95em;
  transition: border-color 0.2s;
}

.chat-input:focus {
  outline: none;
  border-color: #ff9933;
}

.send-btn {
  padding: 12px 20px;
  background: linear-gradient(135deg, #ff9933, #ff6600);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2em;
  transition: transform 0.2s, opacity 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
