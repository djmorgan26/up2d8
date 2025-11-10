/**
 * Zod validation schemas
 */
import { z } from 'zod';

/**
 * Feed validation schema
 */
export const feedSchema = z.object({
  url: z.string().url('Please enter a valid URL'),
  title: z.string().min(1, 'Title is required').optional(),
  category: z.string().optional(),
});

export type FeedFormData = z.infer<typeof feedSchema>;

/**
 * User preferences validation schema
 */
export const userPreferencesSchema = z.object({
  user_id: z.string(),
  topics: z.array(z.string()).min(1, 'Select at least one topic'),
  notification_enabled: z.boolean(),
  theme: z.enum(['light', 'dark', 'system']).optional(),
  language: z.string().optional(),
});

export type UserPreferencesFormData = z.infer<typeof userPreferencesSchema>;

/**
 * Chat message validation schema
 */
export const chatMessageSchema = z.object({
  message: z.string().min(1, 'Message cannot be empty').max(500, 'Message too long (max 500 characters)'),
});

export type ChatMessageFormData = z.infer<typeof chatMessageSchema>;

/**
 * Search params validation schema
 */
export const searchParamsSchema = z.object({
  query: z.string().optional(),
  category: z.string().optional(),
  tag: z.string().optional(),
  sortBy: z.enum(['date', 'relevance']).optional(),
  sortOrder: z.enum(['asc', 'desc']).optional(),
  limit: z.number().min(1).max(100).optional(),
  offset: z.number().min(0).optional(),
});

export type SearchParamsFormData = z.infer<typeof searchParamsSchema>;

/**
 * Topic selection validation schema
 */
export const topicSelectionSchema = z.object({
  topics: z.array(z.string()).min(1, 'Select at least one topic').max(10, 'Maximum 10 topics allowed'),
});

export type TopicSelectionFormData = z.infer<typeof topicSelectionSchema>;

/**
 * Generic email validation
 */
export const emailSchema = z.string().email('Please enter a valid email address');

/**
 * Generic URL validation
 */
export const urlSchema = z.string().url('Please enter a valid URL');
