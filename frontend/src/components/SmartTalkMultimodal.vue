<template>
  <!-- Smart-Talk Multi-Modal Side Panel (Right Sidebar) -->
  <div class="smart-talk-panel" :class="{ 'panel-open': isOpen, 'panel-closed': !isOpen }">
    
    <!-- Toggle Button (Visible when closed) -->
    <button class="toggle-btn" @click="togglePanel" v-if="!isOpen">
      <span class="icon">🤖</span>
      <span class="label">Smart-Talk</span>
    </button>

    <!-- Main Panel Content -->
    <div class="panel-content" v-show="isOpen">
      
      <!-- Header -->
      <div class="panel-header">
        <div class="header-title">
          <span class="flag">🇮🇳</span>
          <h3>Smart-Talk AI</h3>
        </div>
        <div class="header-actions">
          <button @click="toggleSettings" class="icon-btn" title="Settings">⚙️</button>
          <button @click="togglePanel" class="icon-btn close-btn" title="Close">✖️</button>
        </div>
      </div>

      <!-- Settings Panel (Collapsible) -->
      <div class="settings-panel" v-if="showSettings">
        <div class="setting-group">
          <label>Mode (भावना)</label>
          <select v-model="context.mode" class="styled-select">
            <option v-for="mode in modes" :key="mode.id" :value="mode.id">
              {{ mode.icon }} {{ mode.name }}
            </option>
          </select>
        </div>
        
        <div class="setting-group">
          <label>Topic (विषय)</label>
          <select v-model="context.topic" class="styled-select">
            <option v-for="topic in topics" :key="topic" :value="topic">
              {{ topic }}
            </option>
          </select>
        </div>

        <div class="setting-group">
          <label>Language (भाषा)</label>
          <select v-model="context.language" class="styled-select">
            <option v-for="lang in languages" :key="lang.code" :value="lang.code">
              {{ lang.name }}
            </option>
          </select>
        </div>

        <div class="setting-row">
          <div class="setting-group small">
            <label>Age</label>
            <select v-model="context.age_group" class="styled-select small">
              <option v-for="age in ageGroups" :key="age" :value="age">{{ age }}</option>
            </select>
          </div>
          <div class="setting-group small">
            <label>Gender</label>
            <select v-model="context.gender" class="styled-select small">
              <option v-for="g in genders" :key="g" :value="g">{{ g }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Chat Messages Area -->
      <div class="chat-messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="welcome-message">
          <p class="namaste">🙏 नमस्ते! Welcome to Smart-Talk</p>
          <p class="sub-text">Choose a mode and start chatting via text, voice, or file!</p>
          
          <div class="quick-actions">
            <button @click="setQuickMode('cricket')" class="quick-btn cricket">🏏 Cricket</button>
            <button @click="setQuickMode('budget')" class="quick-btn budget">💰 Budget</button>
            <button @click="setQuickMode('festival')" class="quick-btn festival">🎉 Festival</button>
            <button @click="setQuickMode('angry')" class="quick-btn angry">😠 Angry Debate</button>
          </div>
        </div>

        <div v-for="(msg, index) in messages" :key="index" 
             class="message" :class="msg.role">
          <div class="message-avatar">
            {{ msg.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-body">
            <div class="message-meta" v-if="msg.model_used">
              <span class="model-tag">{{ msg.model_used }}</span>
              <span class="time-tag">{{ msg.timestamp }}</span>
            </div>
            <div class="message-content">
              <!-- Render File Preview if exists -->
              <div v-if="msg.filePreview" class="file-preview">
                <img v-if="msg.fileType?.startsWith('image')" :src="msg.filePreview" alt="Uploaded" />
                <div v-else class="file-icon">📄 {{ msg.fileName }}</div>
              </div>
              <p>{{ msg.content }}</p>
            </div>
            <!-- Translation Button -->
            <button v-if="msg.role === 'assistant' && !msg.translated" 
                    @click="translateMessage(msg)" 
                    class="translate-btn" 
                    :title="`Translate to ${context.language}`">
              🌐 Translate
            </button>
            <div v-if="msg.translation" class="translation-box">
              <p><strong>Translation:</strong> {{ msg.translation }}</p>
            </div>
          </div>
        </div>
        
        <div v-if="isLoading" class="message assistant loading">
          <div class="message-avatar">🤖</div>
          <div class="message-body">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
            <p>Thinking... (सोच रहा हूँ)</p>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="input-area">
        <!-- File Upload & Voice Buttons -->
        <div class="input-tools">
          <label class="tool-btn" title="Upload Image/File">
            📎
            <input type="file" ref="fileInput" @change="handleFileUpload" 
                   accept="image/*,.pdf,.csv,.xlsx,.json" hidden />
          </label>
          <button @click="toggleVoiceRecording" class="tool-btn" 
                  :class="{ 'recording': isRecording }" 
                  :title="isRecording ? 'Stop Recording' : 'Start Voice Talk'">
            {{ isRecording ? '🔴' : '🎤' }}
          </button>
        </div>

        <!-- Text Input -->
        <textarea 
          v-model="userInput" 
          @keydown.enter.exact.prevent="sendMessage"
          placeholder="Type your message... (हिंदी or English)"
          rows="2"
        ></textarea>

        <!-- Send Button -->
        <button @click="sendMessage" class="send-btn" :disabled="isLoading || (!userInput.trim() && !selectedFile)">
          ➤
        </button>
      </div>

      <!-- Recording Indicator Overlay -->
      <div v-if="isRecording" class="recording-overlay">
        <div class="pulse-circle"></div>
        <p>Listening... (सुन रहा हूँ)</p>
        <button @click="stopRecording" class="stop-record-btn">Stop</button>
      </div>

    </div>
  </div>
</template>

<script>
import { 
  sendTextMessage, 
  sendVoiceMessage, 
  analyzeFile, 
  analyzeData,
  translateText,
  EMOTIONAL_MODES,
  TOPICS,
  LANGUAGES,
  AGE_GROUPS,
  GENDERS
} from '@/api/chatbot-multimodal';

export default {
  name: 'SmartTalkMultimodal',
  data() {
    return {
      isOpen: true,
      showSettings: false,
      userInput: '',
      messages: [],
      isLoading: false,
      isRecording: false,
      selectedFile: null,
      mediaRecorder: null,
      audioChunks: [],
      
      // Context State
      context: {
        mode: 'neutral',
        topic: 'General',
        language: 'en-IN',
        age_group: 'Millennial',
        gender: 'Other',
        weather: 'Sunny',
        season: 'Summer'
      },

      // Dropdown Options
      modes: EMOTIONAL_MODES,
      topics: TOPICS,
      languages: LANGUAGES,
      ageGroups: AGE_GROUPS,
      genders: GENDERS
    };
  },
  mounted() {
    this.scrollToBottom();
  },
  methods: {
    togglePanel() {
      this.isOpen = !this.isOpen;
    },
    toggleSettings() {
      this.showSettings = !this.showSettings;
    },
    setQuickMode(modeId) {
      this.context.mode = modeId;
      this.showSettings = false;
      this.addSystemMessage(`Switched to ${modeId.toUpperCase()} mode!`);
    },
    addSystemMessage(content) {
      this.messages.push({
        role: 'assistant',
        content,
        timestamp: new Date().toLocaleTimeString(),
        model_used: 'System'
      });
      this.scrollToBottom();
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },
    async sendMessage() {
      if ((!this.userInput.trim() && !this.selectedFile) || this.isLoading) return;

      const messageText = this.userInput.trim();
      const fileToSend = this.selectedFile;
      
      // Clear input
      this.userInput = '';
      this.selectedFile = null;

      // Add User Message to UI
      const userMsg = {
        role: 'user',
        content: messageText || '📎 File: ' + (fileToSend?.name || 'Uploaded'),
        timestamp: new Date().toLocaleTimeString(),
        filePreview: fileToSend ? URL.createObjectURL(fileToSend) : null,
        fileName: fileToSend?.name,
        fileType: fileToSend?.type
      };
      this.messages.push(userMsg);
      this.scrollToBottom();

      this.isLoading = true;

      try {
        let response;
        
        // Determine API call based on input type
        if (fileToSend) {
          if (fileToSend.type.startsWith('image/') || fileToSend.type === 'application/pdf') {
            // Vision Analysis
            response = await analyzeFile(fileToSend, messageText, this.context);
          } else if (['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/json'].includes(fileToSend.type)) {
            // Data Analysis
            response = await analyzeData(fileToSend, messageText, this.context);
          }
        } else {
          // Text Chat
          response = await sendTextMessage(messageText, this.context);
        }

        if (response.success) {
          this.messages.push({
            role: 'assistant',
            content: response.response,
            timestamp: new Date().toLocaleTimeString(),
            model_used: response.model_used,
            type: response.type
          });
        } else {
          throw new Error(response.error || 'Failed to get response');
        }

      } catch (error) {
        console.error('Chat error:', error);
        this.messages.push({
          role: 'assistant',
          content: `Error: ${error.message}. Please try again.`,
          timestamp: new Date().toLocaleTimeString(),
          model_used: 'Error'
        });
      } finally {
        this.isLoading = false;
        this.scrollToBottom();
      }
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
        // Auto-send option could be added here
      }
    },
    toggleVoiceRecording() {
      if (this.isRecording) {
        this.stopRecording();
      } else {
        this.startRecording();
      }
    },
    async startRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream);
        this.audioChunks = [];

        this.mediaRecorder.ondataavailable = (event) => {
          this.audioChunks.push(event.data);
        };

        this.mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
          await this.processVoiceMessage(audioBlob);
        };

        this.mediaRecorder.start();
        this.isRecording = true;
      } catch (error) {
        console.error('Microphone access denied:', error);
        alert('Microphone access required for voice chat!');
      }
    },
    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.mediaRecorder.stop();
        this.isRecording = false;
        // Stop all tracks
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
      }
    },
    async processVoiceMessage(audioBlob) {
      this.isLoading = true;
      
      // Add temporary user voice message
      this.messages.push({
        role: 'user',
        content: '🎤 Voice Message',
        timestamp: new Date().toLocaleTimeString()
      });
      this.scrollToBottom();

      try {
        const response = await sendVoiceMessage(audioBlob, this.context);
        
        if (response.success) {
          this.messages.push({
            role: 'assistant',
            content: response.response,
            timestamp: new Date().toLocaleTimeString(),
            model_used: response.model_used,
            type: 'voice_response'
          });
        } else {
          throw new Error(response.error);
        }
      } catch (error) {
        this.messages.push({
          role: 'assistant',
          content: `Voice Error: ${error.message}`,
          timestamp: new Date().toLocaleTimeString()
        });
      } finally {
        this.isLoading = false;
        this.scrollToBottom();
      }
    },
    async translateMessage(msg) {
      if (!msg.content || msg.translated) return;
      
      try {
        const response = await translateText(msg.content, this.context.language);
        if (response.success) {
          msg.translation = response.translated;
          msg.translated = true;
        }
      } catch (error) {
        console.error('Translation error:', error);
      }
    }
  }
};
</script>

<style scoped>
/* Smart-Talk Side Panel Styles */
.smart-talk-panel {
  position: fixed;
  right: 0;
  top: 0;
  height: 100vh;
  width: 400px;
  background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
  box-shadow: -4px 0 15px rgba(0,0,0,0.1);
  z-index: 9999;
  transition: transform 0.3s ease;
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.panel-closed {
  transform: translateX(100%);
}

/* Toggle Button */
.toggle-btn {
  position: absolute;
  left: -60px;
  top: 50%;
  transform: translateY(-50%);
  background: linear-gradient(135deg, #FF9933, #FFFFFF, #138808); /* Indian Flag */
  border: none;
  padding: 15px 10px;
  border-radius: 10px 0 0 10px;
  cursor: pointer;
  box-shadow: -3px 0 10px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #333;
  font-weight: bold;
}

.toggle-btn .icon { font-size: 24px; }
.toggle-btn .label { font-size: 12px; margin-top: 5px; }

/* Header */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: linear-gradient(90deg, #FF9933, #FFFFFF, #138808);
  border-bottom: 2px solid #ddd;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title .flag { font-size: 24px; }
.header-title h3 { margin: 0; color: #333; font-size: 18px; }

.icon-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 5px;
  border-radius: 5px;
  transition: background 0.2s;
}

.icon-btn:hover { background: rgba(0,0,0,0.1); }

/* Settings Panel */
.settings-panel {
  background: #f1f3f5;
  padding: 15px;
  border-bottom: 1px solid #ddd;
  max-height: 200px;
  overflow-y: auto;
}

.setting-group {
  margin-bottom: 10px;
}

.setting-group label {
  display: block;
  font-size: 12px;
  font-weight: bold;
  color: #555;
  margin-bottom: 5px;
}

.setting-row {
  display: flex;
  gap: 10px;
}

.setting-group.small { flex: 1; }

.styled-select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background: white;
  font-size: 13px;
}

.styled-select.small { font-size: 12px; padding: 6px; }

/* Chat Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  background: #f9f9f9;
}

.welcome-message {
  text-align: center;
  padding: 20px;
  color: #666;
}

.namaste { font-size: 20px; font-weight: bold; color: #FF9933; }
.sub-text { font-size: 14px; margin-top: 5px; }

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 15px;
}

.quick-btn {
  padding: 10px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  color: white;
  transition: transform 0.2s;
}

.quick-btn:hover { transform: scale(1.05); }
.quick-btn.cricket { background: #2E7D32; }
.quick-btn.budget { background: #1976D2; }
.quick-btn.festival { background: #E91E63; }
.quick-btn.angry { background: #D32F2F; }

/* Message Bubbles */
.message {
  display: flex;
  gap: 10px;
  max-width: 90%;
}

.message.user { align-self: flex-end; flex-direction: row-reverse; }
.message.assistant { align-self: flex-start; }

.message-avatar {
  font-size: 24px;
  background: #e0e0e0;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-body {
  background: white;
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  position: relative;
}

.message.user .message-body {
  background: #E3F2FD;
  border-bottom-right-radius: 2px;
}

.message.assistant .message-body {
  border-bottom-left-radius: 2px;
}

.message-meta {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: #888;
  margin-bottom: 5px;
}

.model-tag {
  background: #eee;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: bold;
}

.file-preview img {
  max-width: 100%;
  border-radius: 8px;
  margin-bottom: 8px;
}

.file-icon {
  background: #eee;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 8px;
  font-size: 14px;
}

.translate-btn {
  margin-top: 8px;
  background: none;
  border: 1px solid #2196F3;
  color: #2196F3;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
}

.translate-btn:hover { background: #E3F2FD; }

.translation-box {
  margin-top: 8px;
  padding: 8px;
  background: #FFF3E0;
  border-left: 3px solid #FF9800;
  border-radius: 4px;
  font-size: 13px;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  margin-bottom: 5px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: #888;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Input Area */
.input-area {
  display: flex;
  gap: 10px;
  padding: 15px;
  background: white;
  border-top: 1px solid #ddd;
  align-items: flex-end;
}

.input-tools {
  display: flex;
  gap: 8px;
  flex-direction: column;
}

.tool-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tool-btn:hover { background: #f0f0f0; }
.tool-btn.recording { animation: pulse-red 1s infinite; }

@keyframes pulse-red {
  0% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(244, 67, 54, 0); }
  100% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0); }
}

textarea {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  max-height: 100px;
}

textarea:focus { outline: 2px solid #FF9933; border-color: transparent; }

.send-btn {
  background: linear-gradient(135deg, #FF9933, #FF5722);
  color: white;
  border: none;
  border-radius: 8px;
  width: 45px;
  height: 45px;
  font-size: 20px;
  cursor: pointer;
  transition: transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:hover:not(:disabled) { transform: scale(1.1); }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Recording Overlay */
.recording-overlay {
  position: absolute;
  bottom: 80px;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.8);
  color: white;
  padding: 20px;
  text-align: center;
  border-radius: 10px;
  margin: 0 15px;
}

.pulse-circle {
  width: 50px;
  height: 50px;
  background: red;
  border-radius: 50%;
  margin: 0 auto 10px;
  animation: pulse-red 1s infinite;
}

.stop-record-btn {
  margin-top: 10px;
  background: red;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: bold;
}

/* Responsive */
@media (max-width: 768px) {
  .smart-talk-panel { width: 100%; }
  .toggle-btn { left: -50px; top: auto; bottom: 20px; transform: none; border-radius: 10px 0 0 10px; }
}
</style>
