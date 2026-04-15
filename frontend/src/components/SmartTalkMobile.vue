<template>
  <!-- Mobile-First Smart-Talk Layout -->
  <div class="mobile-layout" :class="[themeMode, { 'safe-area-inset': isMobile }]">
    
    <!-- Theme Toggle (Top-Left Corner) -->
    <div class="theme-toggle-container">
      <button 
        @click="cycleTheme" 
        class="theme-toggle-btn"
        aria-label="Toggle theme (Day/Night/System)"
      >
        <svg v-if="themeMode === 'day'" viewBox="0 0 24 24" width="24" height="24">
          <circle cx="12" cy="12" r="5" fill="#ff9933"/>
          <g stroke="#ff9933" stroke-width="2">
            <line x1="12" y1="1" x2="12" y2="4"/>
            <line x1="12" y1="20" x2="12" y2="23"/>
            <line x1="1" y1="12" x2="4" y2="12"/>
            <line x1="20" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="4.22" x2="6.34" y2="6.34"/>
            <line x1="17.66" y1="17.66" x2="19.78" y2="19.78"/>
            <line x1="4.22" y1="19.78" x2="6.34" y2="17.66"/>
            <line x1="17.66" y1="6.34" x2="19.78" y2="4.22"/>
          </g>
        </svg>
        <svg v-else-if="themeMode === 'night'" viewBox="0 0 24 24" width="24" height="24">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" fill="#ffb74d"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" width="24" height="24">
          <circle cx="12" cy="12" r="10" stroke="#888" stroke-width="2" fill="none"/>
          <path d="M12 2a10 10 0 0 1 0 20" fill="#888" opacity="0.5"/>
        </svg>
      </button>
    </div>

    <!-- Main Content Area -->
    <main class="content-area">
      
      <!-- Landing Page Section (Fixed at Top) -->
      <section class="landing-section" ref="landingSection">
        <div class="hero-content">
          <h1 class="hero-title">Smart-Talk</h1>
          <p class="hero-subtitle">भारतीय शैली में खुली चर्चा | Indian Style Open Discussion</p>
          <div class="quick-stats">
            <div class="stat-item">
              <span class="stat-number">{{ stats.conversations }}</span>
              <span class="stat-label">Conversations</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ stats.images }}</span>
              <span class="stat-label">Images Generated</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ stats.users }}</span>
              <span class="stat-label">Active Users</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Infinite Scroll Data Gallery -->
      <section class="gallery-section" ref="gallerySection">
        <div class="gallery-header">
          <h2>Public Gallery</h2>
          <span class="live-indicator">🔴 Live</span>
        </div>
        
        <div class="gallery-grid" v-if="galleryItems.length > 0">
          <div 
            v-for="(item, index) in visibleItems" 
            :key="item.id"
            class="gallery-card"
            @click="openItem(item)"
          >
            <div class="card-image-container">
              <img 
                :src="item.thumbnail" 
                :alt="item.title"
                loading="lazy"
                class="card-image"
              />
              <div class="card-overlay">
                <span class="card-mode">{{ item.mode }}</span>
              </div>
            </div>
            <div class="card-content">
              <h3 class="card-title">{{ item.title }}</h3>
              <p class="card-preview">{{ item.preview }}</p>
              <div class="card-meta">
                <span class="card-language">{{ item.language }}</span>
                <span class="card-time">{{ formatTime(item.createdAt) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading Skeleton -->
        <div v-if="isLoading" class="loading-skeleton">
          <div v-for="n in 6" :key="n" class="skeleton-card">
            <div class="skeleton-image"></div>
            <div class="skeleton-text short"></div>
            <div class="skeleton-text long"></div>
          </div>
        </div>

        <!-- No More Items -->
        <div v-if="!isLoading && !hasMore" class="no-more-items">
          <p>You've reached the end! 🎉</p>
        </div>

        <!-- Pull to Refresh Indicator -->
        <div v-if="isRefreshing" class="refresh-indicator">
          <div class="spinner"></div>
          <span>Refreshing...</span>
        </div>
      </section>
    </main>

    <!-- Quick Action Bar (Above Orb) -->
    <div class="quick-action-bar">
      <button 
        v-for="action in quickActions" 
        :key="action.id"
        @click="triggerAction(action)"
        @longpress="showActionLabel(action)"
        class="action-btn"
        :aria-label="action.label"
      >
        <span class="action-icon">{{ action.icon }}</span>
      </button>
    </div>

    <!-- Floating Smart-Talk Orb (Bottom-Right) -->
    <div 
      class="smart-talk-orb"
      :class="{ 'expanded': isOrbExpanded }"
      :style="orbPosition"
      @touchstart="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
      @click="toggleOrb"
    >
      <!-- Collapsed State -->
      <div v-show="!isOrbExpanded" class="orb-collapsed">
        <div class="orb-pulse"></div>
        <span class="orb-icon">💬</span>
      </div>

      <!-- Expanded State (Full Screen Modal) -->
      <div v-show="isOrbExpanded" class="orb-expanded">
        <div class="orb-header">
          <div class="orb-mode-selector">
            <button 
              v-for="mode in modes" 
              :key="mode.id"
              @click.stop="selectMode(mode)"
              :class="['mode-btn', { active: currentMode === mode.id }]"
            >
              {{ mode.icon }}
            </button>
          </div>
          <button @click.stop="toggleOrb" class="close-btn">✕</button>
        </div>
        
        <div class="orb-chat-container">
          <div class="chat-messages" ref="chatMessages">
            <div 
              v-for="message in chatMessages" 
              :key="message.id"
              :class="['message', message.sender]"
            >
              <div class="message-bubble">
                <p>{{ message.text }}</p>
                <div v-if="message.image" class="message-image">
                  <img :src="message.image" alt="Generated content" />
                </div>
                <div v-if="message.translation" class="message-translation">
                  <button @click="toggleTranslation(message)">
                    {{ message.showTranslation ? 'Hide' : 'Translate' }}
                  </button>
                  <p v-if="message.showTranslation">{{ message.translation }}</p>
                </div>
                <span class="message-time">{{ formatMessageTime(message.timestamp) }}</span>
              </div>
            </div>
            
            <!-- Typing Indicator -->
            <div v-if="isTyping" class="message ai typing">
              <div class="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>

          <!-- Input Area -->
          <div class="chat-input-area">
            <button @click="startVoiceRecording" class="voice-btn">
              <span v-if="isRecording" class="recording-indicator">🔴</span>
              <span v-else>🎤</span>
            </button>
            <input 
              v-model="userInput"
              @keyup.enter="sendMessage"
              type="text"
              placeholder="Type your message..."
              class="text-input"
            />
            <button @click="attachFile" class="attach-btn">📎</button>
            <button @click="sendMessage" class="send-btn">➤</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Hidden File Input -->
    <input 
      ref="fileInput"
      type="file" 
      @change="handleFileSelect"
      accept="image/*,.pdf,.csv,.xlsx"
      class="hidden"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useIntersectionObserver } from '@vueuse/core';

export default {
  name: 'SmartTalkMobile',
  setup() {
    // Theme Management
    const themeMode = ref('system');
    const cycleTheme = () => {
      const themes = ['day', 'night', 'system'];
      const currentIndex = themes.indexOf(themeMode.value);
      themeMode.value = themes[(currentIndex + 1) % themes.length];
      applyTheme(themeMode.value);
    };

    const applyTheme = (mode) => {
      if (mode === 'system') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
      } else {
        document.documentElement.setAttribute('data-theme', mode);
      }
      localStorage.setItem('smart-talk-theme', mode);
    };

    // Stats
    const stats = ref({
      conversations: 1247,
      images: 892,
      users: 3421
    });

    // Gallery with Infinite Scroll
    const galleryItems = ref([]);
    const visibleItems = ref([]);
    const isLoading = ref(false);
    const hasMore = ref(true);
    const currentPage = ref(1);
    const isRefreshing = ref(false);
    const gallerySection = ref(null);

    const loadGalleryItems = async (page = 1, refresh = false) => {
      if (isLoading.value || (!hasMore.value && !refresh)) return;
      
      isLoading.value = true;
      
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 800));
        
        const newItems = Array.from({ length: 12 }, (_, i) => ({
          id: `${page}-${i}`,
          thumbnail: `https://picsum.photos/400/300?random=${page * 100 + i}`,
          title: ['Cricket Fever', 'Budget Analysis', 'Festival Joy', 'Family Moments'][i % 4],
          preview: 'AI-generated discussion on trending topics...',
          mode: ['cricket', 'budget', 'festival', 'family'][i % 4],
          language: ['हिंदी', 'English', 'தமிழ்', 'తెలుగు'][i % 4],
          createdAt: new Date(Date.now() - i * 3600000)
        }));

        if (refresh) {
          galleryItems.value = newItems;
        } else {
          galleryItems.value = [...galleryItems.value, ...newItems];
        }
        
        visibleItems.value = galleryItems.value.slice(0, page * 12);
        hasMore.value = page < 5; // Limit for demo
        currentPage.value = page;
      } catch (error) {
        console.error('Failed to load gallery:', error);
      } finally {
        isLoading.value = false;
        isRefreshing.value = false;
      }
    };

    // Intersection Observer for Infinite Scroll
    const { stop: stopObserver } = useIntersectionObserver(
      gallerySection,
      ([{ isIntersecting }]) => {
        if (isIntersecting && !isLoading.value) {
          loadGalleryItems(currentPage.value + 1);
        }
      },
      { threshold: 0.1 }
    );

    // Pull to Refresh
    let touchStartY = 0;
    const handleTouchStart = (e) => {
      if (gallerySection.value.scrollTop === 0) {
        touchStartY = e.touches[0].clientY;
      }
    };

    const handleTouchMove = (e) => {
      if (touchStartY && e.touches[0].clientY - touchStartY > 80) {
        isRefreshing.value = true;
        loadGalleryItems(1, true);
        touchStartY = 0;
      }
    };

    // Smart-Talk Orb
    const isOrbExpanded = ref(false);
    const orbX = ref(window.innerWidth - 80);
    const orbY = ref(window.innerHeight - 150);
    const isDragging = ref(false);
    const dragStartX = ref(0);
    const dragStartY = ref(0);

    const orbPosition = computed(() => ({
      left: `${orbX.value}px`,
      top: `${orbY.value}px`
    }));

    const toggleOrb = () => {
      isOrbExpanded.value = !isOrbExpanded.value;
      if (isOrbExpanded.value) {
        nextTick(() => {
          chatMessages.value?.scrollTo({ top: chatMessages.value.scrollHeight, behavior: 'smooth' });
        });
      }
      // Haptic feedback
      if (navigator.vibrate) navigator.vibrate(50);
    };

    const handleTouchStartDrag = (e) => {
      isDragging.value = true;
      dragStartX.value = e.touches[0].clientX - orbX.value;
      dragStartY.value = e.touches[0].clientY - orbY.value;
    };

    const handleTouchMoveDrag = (e) => {
      if (!isDragging.value) return;
      e.preventDefault();
      orbX.value = Math.min(Math.max(20, e.touches[0].clientX - dragStartX.value), window.innerWidth - 80);
      orbY.value = Math.min(Math.max(80, e.touches[0].clientY - dragStartY.value), window.innerHeight - 150);
    };

    const handleTouchEndDrag = () => {
      isDragging.value = false;
    };

    // Chat Functionality
    const chatMessages = ref([
      { id: 1, sender: 'ai', text: 'नमस्ते! मैं Smart-Talk हूँ। आज किस बारे में बात करें?', timestamp: new Date() }
    ]);
    const userInput = ref('');
    const isTyping = ref(false);
    const isRecording = ref(false);
    const currentMode = ref('neutral');
    const chatMessagesRef = ref(null);

    const modes = [
      { id: 'angry', icon: '😠' },
      { id: 'cricket', icon: '🏏' },
      { id: 'budget', icon: '💰' },
      { id: 'festival', icon: '🎉' },
      { id: 'family', icon: '👨‍👩‍👧‍👦' },
      { id: 'neutral', icon: '😐' }
    ];

    const selectMode = (mode) => {
      currentMode.value = mode.id;
      addSystemMessage(`Switched to ${mode.id} mode ${mode.icon}`);
    };

    const sendMessage = async () => {
      if (!userInput.value.trim()) return;

      const userMsg = {
        id: Date.now(),
        sender: 'user',
        text: userInput.value,
        timestamp: new Date()
      };

      chatMessages.value.push(userMsg);
      userInput.value = '';
      isTyping.value = true;

      scrollToBottom();

      // Simulate AI response
      setTimeout(() => {
        const aiMsg = {
          id: Date.now() + 1,
          sender: 'ai',
          text: `यह ${currentMode.value} मोड में आपका संदेश है: "${userMsg.text}"`,
          timestamp: new Date(),
          translation: null,
          showTranslation: false
        };
        chatMessages.value.push(aiMsg);
        isTyping.value = false;
        scrollToBottom();
      }, 1500);
    };

    const addSystemMessage = (text) => {
      chatMessages.value.push({
        id: Date.now(),
        sender: 'system',
        text,
        timestamp: new Date()
      });
      scrollToBottom();
    };

    const scrollToBottom = () => {
      nextTick(() => {
        chatMessagesRef.value?.scrollTo({ top: chatMessagesRef.value.scrollHeight, behavior: 'smooth' });
      });
    };

    const toggleTranslation = (message) => {
      message.showTranslation = !message.showTranslation;
      if (!message.translation) {
        // Simulate translation
        message.translation = 'यह अनुवादित संदेश है...';
      }
    };

    const startVoiceRecording = () => {
      isRecording.value = !isRecording.value;
      if (isRecording.value) {
        // Start recording logic
        if (navigator.vibrate) navigator.vibrate([50, 100, 50]);
      } else {
        // Stop recording and send
        userInput.value = 'Voice message recorded...';
        sendMessage();
      }
    };

    const attachFile = () => {
      this.$refs.fileInput.click();
    };

    const handleFileSelect = (e) => {
      const file = e.target.files[0];
      if (file) {
        addSystemMessage(`File attached: ${file.name}`);
        // Upload and process file
      }
    };

    // Quick Actions
    const quickActions = [
      { id: 'voice', icon: '🎤', label: 'Voice Chat' },
      { id: 'image', icon: '📷', label: 'Generate Image' },
      { id: 'data', icon: '📊', label: 'Analyze Data' },
      { id: 'translate', icon: '🌐', label: 'Translate' }
    ];

    const triggerAction = (action) => {
      switch(action.id) {
        case 'voice': startVoiceRecording(); break;
        case 'image': addSystemMessage('Image generation mode activated'); break;
        case 'data': attachFile(); break;
        case 'translate': addSystemMessage('Translation ready'); break;
      }
    };

    // Utility Functions
    const formatTime = (date) => {
      const now = new Date();
      const diff = now - new Date(date);
      const minutes = Math.floor(diff / 60000);
      if (minutes < 60) return `${minutes}m ago`;
      const hours = Math.floor(minutes / 60);
      if (hours < 24) return `${hours}h ago`;
      return new Date(date).toLocaleDateString();
    };

    const formatMessageTime = (date) => {
      return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const openItem = (item) => {
      // Open item in full view
      console.log('Opening item:', item);
    };

    const showActionLabel = (action) => {
      // Show tooltip with action label
      alert(action.label);
    };

    // Lifecycle
    onMounted(() => {
      // Load saved theme
      const savedTheme = localStorage.getItem('smart-talk-theme') || 'system';
      themeMode.value = savedTheme;
      applyTheme(savedTheme);

      // Initial gallery load
      loadGalleryItems(1);

      // Add event listeners for orb dragging
      const orbElement = document.querySelector('.smart-talk-orb');
      orbElement?.addEventListener('touchstart', handleTouchStartDrag);
      orbElement?.addEventListener('touchmove', handleTouchMoveDrag);
      orbElement?.addEventListener('touchend', handleTouchEndDrag);
    });

    onUnmounted(() => {
      stopObserver();
    });

    return {
      themeMode,
      cycleTheme,
      stats,
      galleryItems,
      visibleItems,
      isLoading,
      hasMore,
      isRefreshing,
      gallerySection,
      loadGalleryItems,
      handleTouchStart,
      handleTouchMove,
      isOrbExpanded,
      orbPosition,
      toggleOrb,
      chatMessages,
      userInput,
      isTyping,
      isRecording,
      currentMode,
      modes,
      selectMode,
      sendMessage,
      toggleTranslation,
      startVoiceRecording,
      attachFile,
      handleFileSelect,
      quickActions,
      triggerAction,
      formatTime,
      formatMessageTime,
      openItem,
      showActionLabel,
      chatMessagesRef
    };
  }
};
</script>

<style scoped>
/* Mobile-First Styles */
.mobile-layout {
  min-height: 100vh;
  background: var(--mobile-bg, #ffffff);
  color: var(--mobile-text, #1a1a1a);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow-x: hidden;
  position: relative;
}

/* Theme Toggle */
.theme-toggle-container {
  position: fixed;
  top: env(safe-area-inset-top, 20px);
  left: 20px;
  z-index: 1000;
}

.theme-toggle-btn {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  transition: transform 0.2s;
}

.theme-toggle-btn:active {
  transform: scale(0.95);
}

[data-theme='dark'] .theme-toggle-btn {
  background: rgba(30, 30, 30, 0.9);
}

/* Content Area */
.content-area {
  padding-top: calc(env(safe-area-inset-top, 20px) + 60px);
  padding-bottom: 120px;
}

/* Landing Section */
.landing-section {
  padding: 40px 20px;
  background: linear-gradient(135deg, #ff9933 0%, #ffffff 50%, #138808 100%);
  text-align: center;
}

.hero-title {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #1a1a1a;
}

.hero-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 24px;
}

.quick-stats {
  display: flex;
  justify-content: space-around;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #1a1a1a;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
}

/* Gallery Section */
.gallery-section {
  padding: 20px;
}

.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.gallery-header h2 {
  font-size: 20px;
  margin: 0;
}

.live-indicator {
  font-size: 12px;
  background: #ff4444;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.gallery-card {
  background: var(--mobile-card-bg, #f5f5f5);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.gallery-card:active {
  transform: scale(0.98);
}

.card-image-container {
  position: relative;
  aspect-ratio: 4/3;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 10px;
}

.card-content {
  padding: 12px;
}

.card-title {
  font-size: 14px;
  font-weight: bold;
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-preview {
  font-size: 12px;
  opacity: 0.7;
  margin: 0 0 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  opacity: 0.6;
}

/* Loading Skeleton */
.loading-skeleton {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.skeleton-card {
  background: var(--mobile-card-bg, #f5f5f5);
  border-radius: 12px;
  overflow: hidden;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: -200px 0; }
  100% { background-position: 200px 0; }
}

.skeleton-image {
  height: 150px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200px 100%;
}

.skeleton-text {
  height: 12px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200px 100%;
  margin: 8px 12px;
  border-radius: 4px;
}

.skeleton-text.short {
  width: 60%;
}

.skeleton-text.long {
  width: 90%;
}

/* Quick Action Bar */
.quick-action-bar {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
  background: rgba(255,255,255,0.95);
  padding: 12px 20px;
  border-radius: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 999;
}

[data-theme='dark'] .quick-action-bar {
  background: rgba(30,30,30,0.95);
}

.action-btn {
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff9933, #ff6600);
  color: white;
  font-size: 20px;
  cursor: pointer;
  transition: transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:active {
  transform: scale(0.9);
}

/* Smart-Talk Orb */
.smart-talk-orb {
  position: fixed;
  z-index: 1000;
  touch-action: none;
}

.orb-collapsed {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff9933, #138808);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  cursor: pointer;
  position: relative;
}

.orb-pulse {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: inherit;
  animation: pulse-orb 2s infinite;
}

@keyframes pulse-orb {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.orb-icon {
  font-size: 24px;
  z-index: 1;
}

.orb-expanded {
  width: 100vw;
  height: 100vh;
  background: var(--mobile-bg, #ffffff);
  display: flex;
  flex-direction: column;
}

.orb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(0,0,0,0.1);
}

.orb-mode-selector {
  display: flex;
  gap: 8px;
  overflow-x: auto;
}

.mode-btn {
  width: 40px;
  height: 40px;
  border: 2px solid transparent;
  border-radius: 50%;
  background: rgba(0,0,0,0.05);
  font-size: 20px;
  cursor: pointer;
  flex-shrink: 0;
}

.mode-btn.active {
  border-color: #ff9933;
  background: rgba(255,153,51,0.2);
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: rgba(0,0,0,0.1);
  font-size: 20px;
  cursor: pointer;
}

.orb-chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  max-width: 80%;
  align-self: flex-start;
}

.message.user {
  align-self: flex-end;
}

.message.system {
  align-self: center;
  max-width: 90%;
  text-align: center;
  font-size: 12px;
  opacity: 0.7;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  background: rgba(0,0,0,0.05);
}

.message.user .message-bubble {
  background: linear-gradient(135deg, #ff9933, #ff6600);
  color: white;
}

.message-bubble p {
  margin: 0 0 8px 0;
  font-size: 15px;
  line-height: 1.4;
}

.message-image img {
  max-width: 100%;
  border-radius: 12px;
  margin-top: 8px;
}

.message-translation {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0,0,0,0.1);
}

.message-translation button {
  background: none;
  border: none;
  color: #ff9933;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
}

.message-translation p {
  margin: 8px 0 0 0;
  font-size: 13px;
  opacity: 0.8;
}

.message-time {
  font-size: 10px;
  opacity: 0.6;
  display: block;
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: rgba(0,0,0,0.3);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input-area {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid rgba(0,0,0,0.1);
  background: var(--mobile-bg, #ffffff);
}

.voice-btn, .attach-btn, .send-btn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: rgba(0,0,0,0.05);
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn {
  background: linear-gradient(135deg, #ff9933, #ff6600);
  color: white;
}

.text-input {
  flex: 1;
  border: 1px solid rgba(0,0,0,0.1);
  border-radius: 22px;
  padding: 0 16px;
  font-size: 15px;
  outline: none;
}

.text-input:focus {
  border-color: #ff9933;
}

.recording-indicator {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.hidden {
  display: none;
}

/* Safe Area Insets */
.safe-area-inset {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

/* Responsive Adjustments */
@media (min-width: 768px) {
  .gallery-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .quick-action-bar {
    bottom: 120px;
  }
}
</style>
