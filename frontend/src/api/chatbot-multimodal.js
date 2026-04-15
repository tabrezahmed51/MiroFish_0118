/**
 * Smart-Talk Multi-Modal Chatbot API Client
 * Supports: Text, Voice, Vision (File Upload), Data Analysis, Translation
 */

import axios from 'axios';

const API_BASE = '/api/chatbot';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Constants for UI Dropdowns ---
export const EMOTIONAL_MODES = [
  { id: 'neutral', name: 'Normal Chat', icon: '😐', color: '#4CAF50' },
  { id: 'angry', name: 'Angry Debate', icon: '😠', color: '#F44336' },
  { id: 'cricket', name: 'Cricket Fan', icon: '🏏', color: '#FF9800' },
  { id: 'budget', name: 'Budget Talk', icon: '💰', color: '#2196F3' },
  { id: 'festival', name: 'Festival Joy', icon: '🎉', color: '#E91E63' },
  { id: 'family_crisis', name: 'Family Support', icon: '🏠', color: '#9C27B0' },
  { id: 'betrayal', name: 'Heartbreak', icon: '💔', color: '#607D8B' },
  { id: 'mourning', name: 'Condolence', icon: '🕯️', color: '#333333' }
];

export const TOPICS = [
  'Sensex', 'Elections', 'Investments', 'Business', 
  'Sports', 'Bollywood', 'Politics', 'Tech', 'General'
];

export const LANGUAGES = [
  { code: 'hi', name: 'Hindi (हिंदी)' },
  { code: 'en-IN', name: 'Indian English' },
  { code: 'bn', name: 'Bengali (বাংলা)' },
  { code: 'ta', name: 'Tamil (தமிழ்)' },
  { code: 'te', name: 'Telugu (తెలుగు)' },
  { code: 'mr', name: 'Marathi (मराठी)' },
  { code: 'gu', name: 'Gujarati (ગુજરાતી)' },
  { code: 'kn', name: 'Kannada (ಕನ್ನಡ)' },
  { code: 'ml', name: 'Malayalam (മലയാളം)' },
  { code: 'pa', name: 'Punjabi (ਪੰਜਾਬੀ)' },
  { code: 'ur', name: 'Urdu (اردو)' }
];

export const AGE_GROUPS = ['Teenage', 'Student', 'Millennial', 'Senior Citizen'];
export const GENDERS = ['Male', 'Female', 'Transgender', 'Other'];
export const WEATHER_TYPES = ['Sunny', 'Cloudy', 'Raining', 'Drizzling', 'Windy'];
export const SEASONS = ['Summer', 'Monsoon', 'Winter', 'Autumn', 'Spring'];

// --- API Functions ---

/**
 * Get available modes, topics, languages configuration
 */
export const getChatConfig = async () => {
  try {
    const response = await api.get('/modes');
    return response.data;
  } catch (error) {
    console.error('Error fetching chat config:', error);
    throw error;
  }
};

/**
 * Send Text Message
 * @param {string} message - User text input
 * @param {object} context - { mode, topic, language, age_group, gender, weather, season }
 */
export const sendTextMessage = async (message, context = {}) => {
  try {
    const response = await api.post('/chat', {
      message,
      ...context
    });
    return response.data;
  } catch (error) {
    console.error('Error sending text message:', error);
    throw error;
  }
};

/**
 * Send Voice Audio File
 * @param {File} audioFile - Audio blob/file from microphone
 * @param {object} context - Context options
 */
export const sendVoiceMessage = async (audioFile, context = {}) => {
  try {
    const formData = new FormData();
    formData.append('audio', audioFile, 'voice_note.webm');
    
    // Append context to form data
    Object.keys(context).forEach(key => {
      formData.append(key, context[key]);
    });

    const response = await api.post('/voice', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error sending voice message:', error);
    throw error;
  }
};

/**
 * Analyze Image/File (Vision)
 * @param {File} file - Image or PDF file
 * @param {string} prompt - User question about the file
 * @param {object} context - Context options
 */
export const analyzeFile = async (file, prompt, context = {}) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('prompt', prompt || 'Analyze this image and give your opinion in Indian style.');
    
    Object.keys(context).forEach(key => {
      formData.append(key, context[key]);
    });

    const response = await api.post('/vision', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing file:', error);
    throw error;
  }
};

/**
 * Analyze Data File (CSV, Excel, JSON)
 * @param {File} file - Data file
 * @param {string} prompt - Specific analysis request
 * @param {object} context - Context options
 */
export const analyzeData = async (file, prompt, context = {}) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('prompt', prompt || 'Analyze this data and provide insights.');
    
    Object.keys(context).forEach(key => {
      formData.append(key, context[key]);
    });

    const response = await api.post('/data', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing data:', error);
    throw error;
  }
};

/**
 * Translate Text to Target Language
 * @param {string} text - Text to translate
 * @param {string} targetLang - Language code (e.g., 'hi', 'ta')
 */
export const translateText = async (text, targetLang) => {
  try {
    const response = await api.post('/translate', {
      text,
      target_lang: targetLang
    });
    return response.data;
  } catch (error) {
    console.error('Error translating text:', error);
    throw error;
  }
};

export default {
  getChatConfig,
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
};
