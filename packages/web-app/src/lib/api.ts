import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "https://up2d8.azurewebsites.net/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
};

// Public endpoints
export const getArticles = () => api.get("/articles");
export const getRSSFeeds = () => api.get("/rss_feeds");

// Protected endpoints
export const addRSSFeed = (url: string, category?: string, title?: string) => api.post("/rss_feeds", { url, category, title });
export const deleteRSSFeed = (feedId: string) => api.delete(`/rss_feeds/${feedId}`);
export const suggestRSSFeeds = (query: string) => api.post("/rss_feeds/suggest", { query });

export const getUser = (userId: string) => api.get(`/users/${userId}`);
export const updateUser = (userId: string, data: any) => api.put(`/users/${userId}`, data);

// Topics
export const suggestTopics = (interests: string[] = [], query: string = "") =>
  api.post("/topics/suggest", { interests, query });

export const sendChatMessage = (sessionId: string, message: string) =>
  api.post(`/sessions/${sessionId}/messages`, { message });

export const getUserSessions = (userId: string) => api.get(`/users/${userId}/sessions`);
export const getSessionMessages = (sessionId: string) => api.get(`/sessions/${sessionId}/messages`);

// Auth endpoint for post-login processing
export const handleLogin = (userProfile: any) => api.post("/auth/login", userProfile);
