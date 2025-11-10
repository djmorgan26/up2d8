/**
 * Topic API endpoints
 */
import type { Topic, SuggestTopicsRequest, SuggestTopicsResponse, ApiResponse } from '@up2d8/shared-types';
import { getApiClient } from '../client';

/**
 * Suggest topics based on interests
 */
export async function suggestTopics(interests: string[] = [], query: string = '') {
  const client = getApiClient();
  const data: SuggestTopicsRequest = { interests, query };
  return client.post<ApiResponse<SuggestTopicsResponse>>('/topics/suggest', data);
}

/**
 * Get all available topics
 */
export async function getTopics() {
  const client = getApiClient();
  return client.get<ApiResponse<Topic[]>>('/topics');
}
