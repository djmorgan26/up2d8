import { GlassCard } from "./GlassCard";
import { Calendar, ExternalLink } from "lucide-react";
import { Button } from "./ui/button";

interface Article {
  id: string;
  title: string;
  description?: string;
  url: string;
  published_at: string;
  source?: string;
}

interface ArticleCardProps {
  article: Article;
}

export const ArticleCard = ({ article }: ArticleCardProps) => {
  const formattedDate = new Date(article.published_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <GlassCard hover className="animate-fade-in">
      <div className="space-y-3">
        <div className="flex items-start justify-between gap-4">
          <h3 className="text-lg font-semibold text-foreground line-clamp-2 flex-1">
            {article.title}
          </h3>
          <Button
            variant="ghost"
            size="icon"
            className="shrink-0 hover:bg-primary/10"
            asChild
          >
            <a href={article.url} target="_blank" rel="noopener noreferrer">
              <ExternalLink className="h-4 w-4" />
            </a>
          </Button>
        </div>

        {article.description && (
          <p className="text-sm text-muted-foreground line-clamp-3">
            {article.description}
          </p>
        )}

        <div className="flex items-center justify-between pt-2 border-t border-border/50">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Calendar className="h-3 w-3" />
            <span>{formattedDate}</span>
          </div>
          {article.source && (
            <span className="text-xs font-medium text-primary">{article.source}</span>
          )}
        </div>
      </div>
    </GlassCard>
  );
};
