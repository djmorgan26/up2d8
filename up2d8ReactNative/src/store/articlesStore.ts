import { create } from 'zustand';
import { Article } from '../types';
import {
  getAllArticles,
  getPersonalizedArticles,
  filterArticlesByTopics,
  sortArticlesByDate,
} from '../services/articlesService';
import { cacheArticles, getCachedArticles } from '../services/storageService';

interface ArticlesState {
  // State
  articles: Article[];
  personalizedArticles: Article[];
  isLoading: boolean;
  error: string | null;
  lastFetched: Date | null;

  // Actions
  fetchArticles: () => Promise<void>;
  fetchPersonalizedArticles: (userTopics: string[]) => Promise<void>;
  loadCachedArticles: () => Promise<void>;
  filterByTopics: (topics: string[]) => void;
  clearArticles: () => void;
  setError: (error: string | null) => void;
}

export const useArticlesStore = create<ArticlesState>((set, get) => ({
  // Initial state
  articles: [],
  personalizedArticles: [],
  isLoading: false,
  error: null,
  lastFetched: null,

  // Fetch all articles from API
  fetchArticles: async () => {
    set({ isLoading: true, error: null });
    try {
      const articles = await getAllArticles();
      const sortedArticles = sortArticlesByDate(articles);

      set({
        articles: sortedArticles,
        isLoading: false,
        lastFetched: new Date(),
      });

      // Cache articles for offline access
      await cacheArticles(sortedArticles);
    } catch (error: any) {
      console.error('[ArticlesStore] Error fetching articles:', error);
      set({
        isLoading: false,
        error: error.message || 'Failed to fetch articles',
      });

      // Try to load cached articles if fetch fails
      await get().loadCachedArticles();
    }
  },

  // Fetch articles personalized for user's topics
  fetchPersonalizedArticles: async (userTopics: string[]) => {
    set({ isLoading: true, error: null });
    try {
      const articles = await getPersonalizedArticles(userTopics);

      set({
        articles,
        personalizedArticles: articles,
        isLoading: false,
        lastFetched: new Date(),
      });

      // Cache articles for offline access
      await cacheArticles(articles);
    } catch (error: any) {
      console.error('[ArticlesStore] Error fetching personalized articles:', error);
      set({
        isLoading: false,
        error: error.message || 'Failed to fetch personalized articles',
      });

      // Try to load cached articles and filter them
      await get().loadCachedArticles();
      get().filterByTopics(userTopics);
    }
  },

  // Load cached articles from storage (for offline access)
  loadCachedArticles: async () => {
    try {
      const cachedArticles = await getCachedArticles();
      if (cachedArticles.length > 0) {
        set({
          articles: cachedArticles,
          isLoading: false,
        });
        console.log('[ArticlesStore] Loaded cached articles');
      }
    } catch (error) {
      console.error('[ArticlesStore] Error loading cached articles:', error);
    }
  },

  // Filter current articles by topics (client-side)
  filterByTopics: (topics: string[]) => {
    const { articles } = get();
    const filtered = filterArticlesByTopics(articles, topics);
    set({ personalizedArticles: filtered });
  },

  // Clear all articles
  clearArticles: () => {
    set({
      articles: [],
      personalizedArticles: [],
      error: null,
      lastFetched: null,
    });
  },

  // Set error manually
  setError: (error: string | null) => {
    set({ error });
  },
}));
