import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, Mail, Sparkles } from 'lucide-react';
import { api } from '../lib/api';
import { Header } from '../components/layout/Header';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import type { Digest } from '../types';

export const DashboardPage: React.FC = () => {
  const [digests, setDigests] = useState<Digest[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDigests();
  }, []);

  const loadDigests = async () => {
    try {
      const data = await api.getDigests(20);
      setDigests(data);
    } catch (error) {
      console.error('Failed to load digests:', error);
    } finally {
      setLoading(false);
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

  const totalArticles = digests.reduce((sum, d) => sum + d.articles.length, 0);

  return (
    <div className="min-h-screen bg-bg-alt">
      <Header />

      {/* Hero Section */}
      <div className="gradient-purple text-white py-16 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-secondary/20"></div>
        <div className="max-w-6xl mx-auto px-4 relative z-10">
          <h1 className="text-5xl font-bold mb-3 tracking-tight">Welcome back!</h1>
          <p className="text-xl opacity-95 font-light">
            Stay up to date with AI-curated industry insights
          </p>
        </div>
      </div>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 -mt-12 mb-12">
          <Card className="border-none shadow-xl hover:shadow-2xl card-hover bg-gradient-to-br from-white to-primary-pale/20">
            <CardContent className="p-8">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-text-secondary mb-2 uppercase tracking-wide">Total Digests</p>
                  <p className="text-4xl font-bold text-text-primary">{digests.length}</p>
                </div>
                <div className="p-4 rounded-xl bg-primary-pale shadow-lg">
                  <Mail className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-none shadow-xl hover:shadow-2xl card-hover bg-gradient-to-br from-white to-secondary-pale/20">
            <CardContent className="p-8">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-text-secondary mb-2 uppercase tracking-wide">Articles Read</p>
                  <p className="text-4xl font-bold text-text-primary">{totalArticles}</p>
                </div>
                <div className="p-4 rounded-xl bg-secondary-pale shadow-lg">
                  <TrendingUp className="h-6 w-6 text-secondary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-none shadow-xl hover:shadow-2xl card-hover bg-gradient-to-br from-white to-primary-pale/20">
            <CardContent className="p-8">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-text-secondary mb-2 uppercase tracking-wide">AI Powered</p>
                  <p className="text-4xl font-bold text-text-primary">100%</p>
                </div>
                <div className="p-4 rounded-xl bg-primary-pale shadow-lg">
                  <Sparkles className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Digests Section */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-text-primary mb-4">Your Digests</h2>
        </div>

        {digests.length === 0 ? (
          <EmptyState
            title="No digests yet"
            message="Your first digest will arrive soon!"
            action={
              <Button variant="primary" onClick={() => navigate('/preferences')}>
                Configure Preferences
              </Button>
            }
          />
        ) : (
          <div className="space-y-4">
            {digests.map((digest) => (
              <Card key={digest.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-semibold text-text-primary mb-1">
                        {new Date(digest.date).toLocaleDateString('en-US', {
                          weekday: 'long',
                          month: 'long',
                          day: 'numeric',
                          year: 'numeric',
                        })}
                      </h3>
                      <p className="text-sm text-text-secondary">
                        {digest.articles.length} articles curated for you
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => navigate(`/digests/${digest.id}`)}
                    >
                      View Digest
                    </Button>
                  </div>

                  <div className="space-y-3">
                    {digest.articles.slice(0, 3).map((item) => (
                      <div
                        key={item.id}
                        className="border-l-4 border-primary pl-4 py-1 hover:bg-bg-soft transition-colors cursor-pointer"
                        onClick={() => navigate(`/digests/${digest.id}`)}
                      >
                        <h4 className="font-medium text-text-primary">
                          {item.article.title}
                        </h4>
                        <p className="text-sm text-text-secondary mt-1">
                          {item.article.source_name}
                        </p>
                      </div>
                    ))}
                    {digest.articles.length > 3 && (
                      <p className="text-sm text-text-tertiary pl-4">
                        +{digest.articles.length - 3} more articles
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};
