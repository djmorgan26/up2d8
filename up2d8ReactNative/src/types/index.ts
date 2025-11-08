// User types
export interface User {
  user_id: string;
  email: string;
  topics: string[];
  created_at: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  newsletter_style?: 'concise' | 'detailed';
}

export interface CreateUserRequest {
  email: string;
  topics: string[];
}

export interface CreateUserResponse {
  message: string;
  user_id: string;
}

export interface UpdateUserRequest {
  topics?: string[];
  preferences?: UserPreferences;
}

export interface UpdateUserResponse {
  message: string;
}

export interface DeleteUserResponse {
  message: string;
}

// Chat types
export interface ChatRequest {
  prompt: string;
}

export interface WebSource {
  web: {
    uri: string;
    title: string;
  };
}

export interface ChatResponse {
  text: string;
  sources: WebSource[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: WebSource[];
  timestamp: Date;
}

// Article types
export interface Article {
  id: string;
  title: string;
  link: string;
  summary: string;
  published: string;
  processed: boolean;
  tags: string[];
  created_at: string;
}

// API Error types
export interface ApiError {
  message: string;
  status?: number;
}

// Available topics (could be fetched from API in the future)
export const AVAILABLE_TOPICS = [
  'Technology',
  'AI',
  'Science',
  'Business',
  'Health',
  'Design',
  'Education',
  'Politics',
  'Environment',
  'Sports',
] as const;

export type TopicType = typeof AVAILABLE_TOPICS[number];
