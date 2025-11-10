import { useEffect, useState } from "react";
import { getArticles, getRSSFeeds } from "@/lib/api";
import { ArticleCard } from "@/components/ArticleCard";
import { ArticleSkeleton } from "@/components/LoadingSkeleton";
import { GlassCard } from "@/components/GlassCard";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Newspaper, Rss, TrendingUp, Clock, MessageSquare, ExternalLink } from "lucide-react";
import { Link } from "react-router-dom";

interface Article {
  id: string;
  title: string;
  description?: string;
  url: string;
  published_at: string;
  source?: string;
}

const Dashboard = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [feedCount, setFeedCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [articlesRes, feedsRes] = await Promise.all([
          getArticles(),
          getRSSFeeds().catch(() => ({ data: { data: [] } }))
        ]);
        setArticles(articlesRes.data.data || []);
        setFeedCount(feedsRes.data?.data?.length || 0);
      } catch (error) {
        console.error("Failed to fetch data:", error);
        toast.error("Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const todayArticles = articles.filter((a) => {
    const articleDate = new Date(a.published_at);
    const today = new Date();
    return articleDate.toDateString() === today.toDateString();
  });

  const recentArticles = articles.slice(0, 6);
  const featuredArticles = articles.slice(0, 3);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div className="hidden md:flex h-12 w-12 rounded-xl bg-gradient-to-br from-primary to-accent items-center justify-center shadow-lg">
            <Newspaper className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">Dashboard</h1>
            <p className="text-sm text-muted-foreground hidden md:block">Your personalized news digest</p>
          </div>
        </div>
        <div className="text-right text-xs md:text-sm text-muted-foreground">
          {new Date().toLocaleDateString("en-US", {
            weekday: "long",
            month: "long",
            day: "numeric"
          })}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <GlassCard className="p-6">
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <Newspaper className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">{articles.length}</p>
              <p className="text-sm text-muted-foreground">Total Articles</p>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center">
              <Rss className="h-6 w-6 text-accent" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">{feedCount}</p>
              <p className="text-sm text-muted-foreground">Active Feeds</p>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-green-500/10 flex items-center justify-center">
              <Clock className="h-6 w-6 text-green-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">{todayArticles.length}</p>
              <p className="text-sm text-muted-foreground">New Today</p>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <Link to="/chat" className="block group">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-lg bg-purple-500/10 flex items-center justify-center group-hover:bg-purple-500/20 transition-colors">
                <MessageSquare className="h-6 w-6 text-purple-500" />
              </div>
              <div>
                <p className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">Ask AI</p>
                <p className="text-sm text-muted-foreground">About your news</p>
              </div>
            </div>
          </Link>
        </GlassCard>
      </div>

      {loading ? (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <ArticleSkeleton key={i} />
            ))}
          </div>
        </div>
      ) : articles.length === 0 ? (
        /* Enhanced Empty State */
        <GlassCard className="p-12 text-center">
          <div className="max-w-md mx-auto space-y-4">
            <div className="h-20 w-20 mx-auto rounded-full bg-muted flex items-center justify-center">
              <Newspaper className="h-10 w-10 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold text-foreground">No articles yet</h3>
            <p className="text-muted-foreground">
              Get started by adding RSS feeds to curate your personalized news digest.
            </p>
            <Button asChild className="mt-4">
              <Link to="/feeds">
                <Rss className="h-4 w-4 mr-2" />
                Add Your First Feed
              </Link>
            </Button>
          </div>
        </GlassCard>
      ) : (
        <>
          {/* Featured Articles */}
          {featuredArticles.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                <h2 className="text-xl font-semibold text-foreground">Featured Stories</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {featuredArticles.map((article) => (
                  <ArticleCard key={article.id || article.url} article={article} />
                ))}
              </div>
            </div>
          )}

          {/* Recent Articles */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-primary" />
                <h2 className="text-xl font-semibold text-foreground">Recent Articles</h2>
              </div>
              {articles.length > 6 && (
                <span className="text-sm text-muted-foreground">
                  Showing {recentArticles.length} of {articles.length}
                </span>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recentArticles.map((article) => (
                <ArticleCard key={article.id || article.url} article={article} />
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
