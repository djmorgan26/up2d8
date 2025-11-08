import { apiClient } from './api';
import { Article } from '../types';

/**
 * Articles Service - Fetches news articles from the backend
 */

/**
 * Get all articles
 * @returns Array of all articles
 */
export const getAllArticles = async (): Promise<Article[]> => {
  try {
    const response = await apiClient.get<Article[]>('/api/articles');
    console.log(`[ArticlesService] Fetched ${response.length} articles`);
    return response;
  } catch (error) {
    console.error('[ArticlesService] Error fetching articles:', error);
    throw error;
  }
};

/**
 * Get a single article by ID
 * @param articleId - Article's unique ID
 * @returns Article details
 */
export const getArticle = async (articleId: string): Promise<Article> => {
  if (!articleId) {
    throw new Error('Article ID is required');
  }

  try {
    const response = await apiClient.get<Article>(`/api/articles/${articleId}`);
    console.log('[ArticlesService] Fetched article:', response.title);
    return response;
  } catch (error) {
    console.error('[ArticlesService] Error fetching article:', error);
    throw error;
  }
};

/**
 * Filter articles by user's topics
 * @param articles - Array of all articles
 * @param userTopics - Array of user's interested topics
 * @returns Filtered array of articles matching user's topics
 */
export const filterArticlesByTopics = (
  articles: Article[],
  userTopics: string[]
): Article[] => {
  if (!userTopics || userTopics.length === 0) {
    return articles;
  }

  // Normalize topics to lowercase for case-insensitive matching
  const normalizedUserTopics = userTopics.map(topic => topic.toLowerCase());

  return articles.filter(article => {
    // Check if any of the article's tags match the user's topics
    return article.tags.some(tag =>
      normalizedUserTopics.includes(tag.toLowerCase())
    );
  });
};

/**
 * Sort articles by published date (most recent first)
 * @param articles - Array of articles
 * @returns Sorted array of articles
 */
export const sortArticlesByDate = (articles: Article[]): Article[] => {
  return [...articles].sort((a, b) => {
    const dateA = new Date(a.published).getTime();
    const dateB = new Date(b.published).getTime();
    return dateB - dateA; // Most recent first
  });
};

/**
 * Get personalized articles for a user
 * @param userTopics - User's interested topics
 * @returns Filtered and sorted articles
 */
export const getPersonalizedArticles = async (
  userTopics: string[]
): Promise<Article[]> => {
  try {
    const allArticles = await getAllArticles();
    const filteredArticles = filterArticlesByTopics(allArticles, userTopics);
    const sortedArticles = sortArticlesByDate(filteredArticles);

    console.log(
      `[ArticlesService] Personalized: ${sortedArticles.length} articles from ${allArticles.length} total`
    );

    return sortedArticles;
  } catch (error) {
    console.error('[ArticlesService] Error getting personalized articles:', error);
    throw error;
  }
};

/**
 * Format relative time (e.g., "2 hours ago")
 * @param dateString - ISO date string
 * @returns Human-readable relative time
 */
export const getRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return 'just now';
  }

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes}m ago`;
  }

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours}h ago`;
  }

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays}d ago`;
  }

  // Return formatted date for older articles
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
};
