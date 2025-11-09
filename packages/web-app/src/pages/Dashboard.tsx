import { useEffect, useState } from "react";
import { getArticles } from "@/lib/api";
import { ArticleCard } from "@/components/ArticleCard";
import { ArticleSkeleton } from "@/components/LoadingSkeleton";
import { toast } from "sonner";
import { Newspaper } from "lucide-react";

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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const response = await getArticles();
        setArticles(response.data);
      } catch (error) {
        console.error("Failed to fetch articles:", error);
        toast.error("Failed to load articles");
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-3">
        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
          <Newspaper className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">Your personalized news feed</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <>
            {[...Array(6)].map((_, i) => (
              <ArticleSkeleton key={i} />
            ))}
          </>
        ) : articles.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <p className="text-muted-foreground">No articles available yet</p>
          </div>
        ) : (
          articles.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))
        )}
      </div>
    </div>
  );
};

export default Dashboard;
