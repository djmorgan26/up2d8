/**
 * Chat/AI-related types
 */

export interface Message {
  id: string;
  text: string;
  content?: string; // Alias for text
  isUser: boolean;
  role?: 'user' | 'assistant'; // Alternative to isUser
  timestamp: Date | string;
  created_at?: string; // Alias for timestamp
  sources?: MessageSource[];
}

export interface MessageSource {
  web?: {
    uri: string;
    title: string;
  };
  url?: string;
  title?: string;
}

export interface ChatSession {
  id: string;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface SendMessageRequest {
  message: string;
  session_id?: string;
}

export interface SendMessageResponse {
  text: string;
  sources?: MessageSource[];
  session_id?: string;
}
