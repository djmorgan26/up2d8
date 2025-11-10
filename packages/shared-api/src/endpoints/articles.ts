/**
 * Article API endpoints
 */
import type { Article, ArticleSearchParams, ApiResponse } from '@up2d8/shared-types';
import { getApiClient } from '../client';

/**
 * Get all articles
 */
export async function getArticles() {
  const client = getApiClient();
  return client.get<ApiResponse<Article[]>>('/articles');
}

/**
 * Get article by ID
 */
export async function getArticle(id: string) {
  const client = getApiClient();
  return client.get<ApiResponse<Article>>(`/articles/${id}`);
}

/**
 * Search articles
 */
export async function searchArticles(params: ArticleSearchParams) {
  const client = getApiClient();
  return client.post<ApiResponse<Article[]>>('/articles/search', params);
}

/**
 * Mark article as read
 */
export async function markArticleAsRead(id: string) {
  const client = getApiClient();
  return client.post<ApiResponse<void>>(`/articles/${id}/read`);
}

/**
 * Bookmark article
 */
export async function bookmarkArticle(id: string) {
  const client = getApiClient();
  return client.post<ApiResponse<void>>(`/articles/${id}/bookmark`);
}

/**
 * Unbookmark article
 */
export async function unbookmarkArticle(id: string) {
  const client = getApiClient();
  return client.delete<ApiResponse<void>>(`/articles/${id}/bookmark`);
}
