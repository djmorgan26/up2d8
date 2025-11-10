/**
 * UP2D8 Shared API Client
 * Centralized API client for web and mobile apps
 */

// Export client
export * from './client';

// Export all endpoints
export * from './endpoints/articles';
export * from './endpoints/feeds';
export * from './endpoints/chat';
export * from './endpoints/users';
export * from './endpoints/topics';
export * from './endpoints/auth';

// Re-export types for convenience
export type { Article, Feed, Message, User, ApiResponse } from '@up2d8/shared-types';
