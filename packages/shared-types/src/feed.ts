/**
 * RSS Feed-related types
 */

export interface Feed {
  id: string;
  url: string;
  title?: string;
  category?: string;
  created_at?: string;
  updated_at?: string;
  last_fetched?: string;
  article_count?: number;
}

export interface SuggestedFeed {
  title: string;
  url: string;
  category: string;
  description?: string;
}

export interface AddFeedRequest {
  url: string;
  title?: string;
  category?: string;
}

export interface UpdateFeedRequest {
  title?: string;
  category?: string;
}
