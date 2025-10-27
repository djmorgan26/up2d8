import React from 'react';
import { ExternalLink, MessageSquare, ThumbsUp, ThumbsDown } from 'lucide-react';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { Card, CardContent } from '../ui/Card';
import type { Article } from '../../types';

interface ArticleCardProps {
  article: Article;
  onAskAI?: () => void;
  showFeedback?: boolean;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({
  article,
  onAskAI,
  showFeedback = false,
}) => {
  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        {/* Header with source and impact */}
        <div className="flex items-start justify-between mb-3">
          <Badge variant="company">{article.source_name}</Badge>
          {article.impact_score && (
            <span className="text-sm font-medium text-primary">
              Impact: {article.impact_score}/10
            </span>
          )}
        </div>

        {/* Title */}
        <h3 className="text-xl font-semibold text-text-primary mb-2 hover:text-primary transition-colors">
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            {article.title}
          </a>
        </h3>

        {/* Metadata */}
        <div className="flex items-center gap-3 text-sm text-text-secondary mb-3">
          {article.author && <span>{article.author}</span>}
          <span>•</span>
          <span>{formatDate(article.published_at)}</span>
        </div>

        {/* Summary */}
        <p className="text-text-secondary mb-4 leading-relaxed">
          {article.summary || article.content?.substring(0, 200) + '...'}
        </p>

        {/* Tags */}
        {(article.companies_mentioned.length > 0 || article.categories.length > 0) && (
          <div className="flex flex-wrap gap-2 mb-4">
            {article.companies_mentioned.map((company) => (
              <Badge key={company} variant="default">
                {company}
              </Badge>
            ))}
            {article.categories.map((category) => (
              <Badge key={category} variant="category">
                {category}
              </Badge>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-3 pt-4 border-t border-border-light">
          <Button
            variant="outline"
            size="sm"
            onClick={() => window.open(article.url, '_blank')}
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Read Full Article
          </Button>

          {onAskAI && (
            <Button variant="ghost" size="sm" onClick={onAskAI}>
              <MessageSquare className="h-4 w-4 mr-2" />
              Ask AI
            </Button>
          )}

          {showFeedback && (
            <div className="ml-auto flex items-center gap-2">
              <button className="p-2 hover:bg-bg-soft rounded-lg transition-colors">
                <ThumbsUp className="h-4 w-4 text-text-secondary" />
              </button>
              <button className="p-2 hover:bg-bg-soft rounded-lg transition-colors">
                <ThumbsDown className="h-4 w-4 text-text-secondary" />
              </button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
