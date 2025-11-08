import { apiClient } from './api';
import { ChatRequest, ChatResponse } from '../types';

/**
 * Chat Service - Interfaces with Gemini AI via backend API
 */

/**
 * Send a message to the AI and get a response with sources
 * @param prompt - The user's message/question
 * @returns AI response with text and web sources
 */
export const sendChatMessage = async (prompt: string): Promise<ChatResponse> => {
  if (!prompt || prompt.trim().length === 0) {
    throw new Error('Prompt cannot be empty');
  }

  const request: ChatRequest = {
    prompt: prompt.trim(),
  };

  try {
    const response = await apiClient.post<ChatResponse>('/api/chat', request);

    // Ensure sources is always an array (backend may return undefined)
    return {
      text: response.text,
      sources: response.sources || [],
    };
  } catch (error) {
    console.error('[ChatService] Error sending message:', error);
    throw error;
  }
};

/**
 * Example prompts to show users
 */
export const EXAMPLE_PROMPTS = [
  "What's the latest news in AI?",
  "Summarize today's tech headlines",
  "Tell me about recent scientific discoveries",
  "What's happening in the business world?",
  "Give me a health news update",
];
