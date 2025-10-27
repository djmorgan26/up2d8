// User types
export interface User {
  id: string;
  email: string;
  full_name: string;
  tier: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'paused' | 'suspended' | 'deleted';
  onboarding_completed: boolean;
  created_at: string;
  last_login_at: string | null;
}

// Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface AuthResponse extends AuthTokens {
  user: User;
  token_type: string;
}

// Article types
export interface Article {
  id: string;
  title: string;
  url: string;
  content: string;
  summary: string | null;
  author: string | null;
  published_at: string;
  source_name: string;
  source_url: string;
  categories: string[];
  companies_mentioned: string[];
  impact_score: number | null;
  created_at: string;
}

// Digest types
export interface DigestArticle {
  id: string;
  digest_id: string;
  article_id: string;
  article: Article;
  position: number;
  relevance_score: number;
  personalization_reason: string | null;
}

export interface Digest {
  id: string;
  user_id: string;
  date: string;
  status: 'draft' | 'sent' | 'failed';
  articles: DigestArticle[];
  created_at: string;
  sent_at: string | null;
}

// Chat types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  follow_up_questions?: string[];
  created_at: string;
}

export interface Citation {
  title: string;
  url: string;
  source: string;
}

export interface ChatSession {
  id: string;
  user_id: string;
  digest_id: string | null;
  created_at: string;
}

// User Preferences
export interface UserPreference {
  id: string;
  user_id: string;
  industries: string[];
  companies_to_track: string[];
  role: string | null;
  topics_of_interest: string[];
  email_time: string;
  email_frequency: 'daily' | 'weekly';
  created_at: string;
  updated_at: string;
}
