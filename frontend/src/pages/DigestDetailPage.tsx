import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MessageSquare, ArrowLeft } from 'lucide-react';
import { api } from '../lib/api';
import { Header } from '../components/layout/Header';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ArticleCard } from '../components/digest/ArticleCard';
import { Button } from '../components/ui/Button';
import type { Digest } from '../types';

export const DigestDetailPage: React.FC = () => {
  const { digestId } = useParams<{ digestId: string }>();
  const navigate = useNavigate();
  const [digest, setDigest] = useState<Digest | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDigest();
  }, [digestId]);

  const loadDigest = async () => {
    if (!digestId) return;

    try {
      const data = await api.getDigest(digestId);
      setDigest(data);
    } catch (error) {
      console.error('Failed to load digest:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAskAI = async (articleId?: string) => {
    try {
      const session = await api.createChatSession(digestId);
      navigate(`/chat/${session.id}`);
    } catch (error) {
      console.error('Failed to create chat session:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header />
        <LoadingSpinner className="mt-20" />
      </div>
    );
  }

  if (!digest) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <p className="text-center text-text-secondary">Digest not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-alt">
      <Header />

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Back button */}
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-text-secondary hover:text-primary mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </button>

        {/* Digest header */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-border-light mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-text-primary mb-2">
                {new Date(digest.date).toLocaleDateString('en-US', {
                  weekday: 'long',
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </h1>
              <p className="text-text-secondary">
                {digest.articles.length} articles curated for you
              </p>
            </div>

            <Button variant="primary" onClick={() => handleAskAI()}>
              <MessageSquare className="h-4 w-4 mr-2" />
              Ask AI
            </Button>
          </div>
        </div>

        {/* Articles */}
        <div className="space-y-4">
          {digest.articles.map((item) => (
            <ArticleCard
              key={item.id}
              article={item.article}
              onAskAI={() => handleAskAI(item.article.id)}
              showFeedback={true}
            />
          ))}
        </div>
      </main>
    </div>
  );
};
