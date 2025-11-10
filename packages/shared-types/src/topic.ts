/**
 * Topic-related types
 */

export interface Topic {
  id: string;
  name: string;
  description?: string;
  category?: string;
}

export interface SuggestTopicsRequest {
  interests?: string[];
  query?: string;
}

export interface SuggestTopicsResponse {
  topics: Topic[];
}
