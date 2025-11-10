/**
 * Article-related types
 */

export interface Article {
  id: string;
  title: string;
  description?: string;
  summary?: string;
  url: string;
  link?: string; // Alias for url
  published_at: string;
  published?: string; // Alias for published_at
  source?: string;
  feed_id?: string;
  tags?: string[];
  author?: string;
  image_url?: string;
  read?: boolean;
  bookmarked?: boolean;
}

export interface ArticleFilters {
  category?: string;
  tag?: string;
  source?: string;
  read?: boolean;
  bookmarked?: boolean;
  dateFrom?: string;
  dateTo?: string;
}

export interface ArticleSearchParams {
  query?: string;
  filters?: ArticleFilters;
  limit?: number;
  offset?: number;
  sortBy?: 'date' | 'relevance';
  sortOrder?: 'asc' | 'desc';
}
