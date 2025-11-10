/**
 * RSS Feed API endpoints
 */
import type { Feed, SuggestedFeed, AddFeedRequest, UpdateFeedRequest, ApiResponse } from '@up2d8/shared-types';
import { getApiClient } from '../client';

/**
 * Get all RSS feeds
 */
export async function getRSSFeeds() {
  const client = getApiClient();
  return client.get<ApiResponse<Feed[]>>('/rss_feeds');
}

/**
 * Get RSS feed by ID
 */
export async function getRSSFeed(id: string) {
  const client = getApiClient();
  return client.get<ApiResponse<Feed>>(`/rss_feeds/${id}`);
}

/**
 * Add new RSS feed
 */
export async function addRSSFeed(url: string, category?: string, title?: string) {
  const client = getApiClient();
  const data: AddFeedRequest = { url, category, title };
  return client.post<ApiResponse<Feed>>('/rss_feeds', data);
}

/**
 * Update RSS feed
 */
export async function updateRSSFeed(feedId: string, data: UpdateFeedRequest) {
  const client = getApiClient();
  return client.put<ApiResponse<Feed>>(`/rss_feeds/${feedId}`, data);
}

/**
 * Delete RSS feed
 */
export async function deleteRSSFeed(feedId: string) {
  const client = getApiClient();
  return client.delete<ApiResponse<void>>(`/rss_feeds/${feedId}`);
}

/**
 * Get AI-powered RSS feed suggestions
 */
export async function suggestRSSFeeds(query: string) {
  const client = getApiClient();
  return client.post<ApiResponse<{ suggestions: SuggestedFeed[] }>>('/rss_feeds/suggest', { query });
}
