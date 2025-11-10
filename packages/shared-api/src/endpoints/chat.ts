/**
 * Chat/AI API endpoints
 */
import type { Message, ChatSession, SendMessageRequest, SendMessageResponse, ApiResponse } from '@up2d8/shared-types';
import { getApiClient } from '../client';

/**
 * Send chat message
 */
export async function sendChatMessage(sessionId: string, message: string) {
  const client = getApiClient();
  const data: SendMessageRequest = { message };
  return client.post<ApiResponse<SendMessageResponse>>(`/sessions/${sessionId}/messages`, data);
}

/**
 * Get user chat sessions
 */
export async function getUserSessions(userId: string) {
  const client = getApiClient();
  return client.get<ApiResponse<ChatSession[]>>(`/users/${userId}/sessions`);
}

/**
 * Get session messages
 */
export async function getSessionMessages(sessionId: string) {
  const client = getApiClient();
  return client.get<ApiResponse<Message[]>>(`/sessions/${sessionId}/messages`);
}

/**
 * Create new chat session
 */
export async function createChatSession(userId: string, title?: string) {
  const client = getApiClient();
  return client.post<ApiResponse<ChatSession>>(`/users/${userId}/sessions`, { title });
}

/**
 * Delete chat session
 */
export async function deleteChatSession(sessionId: string) {
  const client = getApiClient();
  return client.delete<ApiResponse<void>>(`/sessions/${sessionId}`);
}
