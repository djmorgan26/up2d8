/**
 * Shared constants for the application
 */

export const TOPIC_CATEGORIES = [
  { id: "technology", label: "Technology", description: "Tech news, gadgets, software, and innovations" },
  { id: "business", label: "Business", description: "Markets, finance, entrepreneurship, and economics" },
  { id: "science", label: "Science", description: "Research, discoveries, and scientific breakthroughs" },
  { id: "health", label: "Health", description: "Medical news, wellness, and healthcare" },
  { id: "sports", label: "Sports", description: "Athletics, competitions, and sports news" },
  { id: "entertainment", label: "Entertainment", description: "Movies, music, celebrities, and pop culture" },
  { id: "politics", label: "Politics", description: "Government, policy, and political news" },
  { id: "world", label: "World News", description: "International news and global events" },
  { id: "environment", label: "Environment", description: "Climate, sustainability, and environmental issues" },
  { id: "education", label: "Education", description: "Learning, schools, and educational developments" },
  { id: "travel", label: "Travel", description: "Destinations, tourism, and travel tips" },
  { id: "food", label: "Food & Dining", description: "Restaurants, recipes, and culinary trends" },
] as const;

export type TopicId = typeof TOPIC_CATEGORIES[number]["id"];
