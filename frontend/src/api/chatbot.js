// Smart-Talk Chatbot API Client
// Qwen AI powered Indian-style open discussion platform

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

/**
 * Smart-Talk Chatbot API Service
 */
export const chatbotAPI = {
  /**
   * Send a chat message with Smart-Talk context
   * @param {Object} params - Chat parameters
   * @param {string} params.message - User message
   * @param {string} params.mode - Emotional mode (angry, cricket_excitement, etc.)
   * @param {string} params.topic - Topic (sensex, elections, sports, etc.)
   * @param {string} params.weather - Weather context (raining, sunny, etc.)
   * @param {string} params.season - Season (winter, monsoon, summer, autumn)
   * @param {string} params.age_group - Age group (teenage, millennial, etc.)
   * @param {string} params.gender - Gender perspective
   * @param {string} params.language - Language (hi, en-IN, en)
   * @param {Array} params.conversation_history - Previous messages
   * @returns {Promise<Object>} Chat response
   */
  async chat(params) {
    const response = await fetch(`${API_BASE_URL}/chatbot/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Chat request failed');
    }
    
    return response.json();
  },

  /**
   * Quick chat with preset configurations
   * @param {string} message - User message
   * @param {string} preset - Preset type (casual, cricket, budget, festival, serious)
   * @param {string} language - Language preference
   * @returns {Promise<Object>} Chat response
   */
  async quickChat(message, preset = 'casual', language = 'hi') {
    return this.chat({
      message,
      preset,
      language,
    });
  },

  /**
   * Get all available modes and configurations
   * @returns {Promise<Object>} Available modes, topics, age groups, etc.
   */
  async getModes() {
    const response = await fetch(`${API_BASE_URL}/chatbot/modes`, {
      method: 'GET',
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch modes');
    }
    
    return response.json();
  },

  /**
   * Health check
   * @returns {Promise<Object>} Service status
   */
  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/chatbot/health`, {
      method: 'GET',
    });
    
    return response.json();
  },
};

/**
 * Smart-Talk Emotional Modes
 */
export const EMOTIONAL_MODES = {
  ANGRY: 'angry',
  CRICKET_EXCITEMENT: 'cricket_excitement',
  BUDGET_DISCUSSION: 'budget_discussion',
  FESTIVAL_HAPPY: 'festival_happy',
  FAMILY_DEVASTATION: 'family_devastation',
  BETRAYAL_SADNESS: 'betrayal_sadness',
  MOURNING: 'mourning',
  NEUTRAL: 'neutral',
};

/**
 * Smart-Talk Topics
 */
export const TOPICS = {
  SENSEX: 'sensex',
  ELECTIONS: 'elections',
  INVESTMENTS: 'investments',
  BUSINESS: 'business',
  SPORTS: 'sports',
  WEATHER_RAINING: 'weather_raining',
  WEATHER_DRIZZLING: 'weather_drizzling',
  WEATHER_SUNNY: 'weather_sunny',
  WEATHER_CLOUDY: 'weather_cloudy',
  SEASON_WINTER: 'season_winter',
  SEASON_MONSOON: 'season_monsoon',
  SEASON_SUMMER: 'season_summer',
  SEASON_AUTUMN: 'season_autumn',
};

/**
 * Age Groups
 */
export const AGE_GROUPS = {
  TEENAGE: 'teenage',
  STUDENT_POSTGRAD: 'student_postgrad',
  MILLENNIAL: 'millennial',
  SENIOR_CITIZEN: 'senior_citizen',
};

/**
 * Gender Perspectives
 */
export const GENDER_PERSPECTIVES = {
  MALE: 'male',
  FEMALE: 'female',
  TRANSGENDER: 'transgender',
  OTHER: 'other',
};

/**
 * Languages
 */
export const LANGUAGES = {
  HINDI: 'hi',
  INDIAN_ENGLISH: 'en-IN',
  ENGLISH: 'en',
};

/**
 * Quick Chat Presets
 */
export const QUICK_CHAT_PRESETS = {
  CASUAL: 'casual',
  CRICKET: 'cricket',
  BUDGET: 'budget',
  FESTIVAL: 'festival',
  SERIOUS: 'serious',
};

export default chatbotAPI;
