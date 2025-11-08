/**
 * Mock data for offline/demo mode
 * Used when backend is unavailable
 */

import { Article, ChatResponse, User } from '../types';

// Mock Articles
export const MOCK_ARTICLES: Article[] = [
  {
    id: 'mock-1',
    title: 'Breakthrough in AI Research: New Language Model Surpasses Expectations',
    link: 'https://example.com/ai-breakthrough',
    summary: 'Researchers have developed a new AI language model that demonstrates unprecedented understanding of context and nuance.',
    published: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    processed: true,
    tags: ['AI', 'Technology', 'Research'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'mock-2',
    title: 'Climate Change Summit: World Leaders Commit to New Targets',
    link: 'https://example.com/climate-summit',
    summary: 'Major nations announce ambitious new climate targets at the annual environmental summit.',
    published: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    processed: true,
    tags: ['Environment', 'Politics', 'Science'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'mock-3',
    title: 'Tech Giants Announce Partnership for Quantum Computing',
    link: 'https://example.com/quantum-partnership',
    summary: 'Leading technology companies join forces to accelerate quantum computing development.',
    published: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
    processed: true,
    tags: ['Technology', 'Business', 'Science'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'mock-4',
    title: 'New Study Reveals Benefits of Mediterranean Diet',
    link: 'https://example.com/mediterranean-diet',
    summary: 'Long-term study shows significant health benefits from following a Mediterranean-style eating pattern.',
    published: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
    processed: true,
    tags: ['Health', 'Science', 'Lifestyle'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'mock-5',
    title: 'Space Agency Plans Mission to Jupiter\'s Moons',
    link: 'https://example.com/jupiter-mission',
    summary: 'New spacecraft will explore the potentially habitable moons of Jupiter in search of signs of life.',
    published: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    processed: true,
    tags: ['Space', 'Science', 'Technology'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'mock-6',
    title: 'Market Update: Tech Stocks Rally on Strong Earnings',
    link: 'https://example.com/tech-stocks-rally',
    summary: 'Technology sector sees significant gains following better-than-expected quarterly earnings reports.',
    published: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    processed: true,
    tags: ['Business', 'Technology', 'Finance'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'mock-7',
    title: 'Breakthrough in Renewable Energy Storage',
    link: 'https://example.com/energy-storage',
    summary: 'Scientists develop new battery technology that could revolutionize renewable energy storage.',
    published: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    processed: true,
    tags: ['Science', 'Technology', 'Environment'],
    created_at: new Date().toISOString(),
  },
  {
    id: 'mock-8',
    title: 'Education Reform: New Approach to Digital Learning',
    link: 'https://example.com/digital-learning',
    summary: 'Schools adopt innovative digital learning methods with promising early results.',
    published: new Date(Date.now() - 10 * 60 * 60 * 1000).toISOString(),
    processed: true,
    tags: ['Education', 'Technology', 'Society'],
    created_at: new Date().toISOString(),
  },
];

// Mock Chat Responses
export const getMockChatResponse = (prompt: string): ChatResponse => {
  const responses: { [key: string]: string } = {
    'default': 'This is a demo response since the backend is offline. Your actual backend will provide AI-powered responses via Google Gemini. Set up your backend and configure the API endpoint in the app settings.',
    'ai': 'Recent developments in artificial intelligence include advances in large language models, improved reasoning capabilities, and better alignment techniques. Major tech companies continue to invest heavily in AI research and development.',
    'tech': 'The technology sector is experiencing rapid innovation in areas like AI, quantum computing, and renewable energy. Recent earnings reports show strong growth in cloud computing and software services.',
    'news': 'Today\'s top headlines cover a range of topics including technology breakthroughs, environmental initiatives, and global economic updates. Check the Browse tab for the latest articles.',
    'health': 'Recent health research highlights the importance of balanced nutrition, regular exercise, and adequate sleep. New studies continue to explore the benefits of preventive care and healthy lifestyle choices.',
  };

  // Find a matching response based on keywords
  const lowerPrompt = prompt.toLowerCase();
  let response = responses['default'];

  for (const [key, value] of Object.entries(responses)) {
    if (lowerPrompt.includes(key)) {
      response = value;
      break;
    }
  }

  return {
    text: `[DEMO MODE] ${response}`,
    sources: [
      {
        web: {
          uri: 'https://example.com/demo',
          title: 'Demo Source - Connect backend for real sources'
        }
      }
    ]
  };
};

// Mock User
export const MOCK_USER: User = {
  user_id: 'mock-user-1',
  email: 'demo@example.com',
  topics: ['Technology', 'AI', 'Science'],
  preferences: {
    newsletter_style: 'concise'
  },
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

// Simulate network delay for realistic feel
export const simulateNetworkDelay = async (ms: number = 500): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};
