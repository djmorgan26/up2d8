/**
 * Dashboard Screen
 * Main dashboard with stats, featured articles, and recent articles
 */

import React from 'react';
import {View, Text, ScrollView, StyleSheet, RefreshControl, Pressable, Alert} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {GlassCard, GlassButton, Skeleton} from '@components/ui';
import {ArticleCard} from '@components/features/ArticleCard';
import {useQuery} from '@tanstack/react-query';
import {getArticles, getRSSFeeds} from '@up2d8/shared-api';
import {Article} from '@up2d8/shared-types';
import {
  Newspaper,
  Rss,
  TrendingUp,
  Clock,
  MessageSquare,
} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';

interface DashboardScreenProps {
  navigation: any;
}

export default function DashboardScreen({navigation}: DashboardScreenProps) {
  const {theme} = useTheme();

  // Fetch articles
  const {
    data: articlesData,
    isLoading: articlesLoading,
    refetch: refetchArticles,
  } = useQuery({
    queryKey: ['articles'],
    queryFn: async () => {
      const response = await getArticles();
      return response.data.data || [];
    },
    retry: 1,
  });

  // Fetch feeds count
  const {data: feedsData} = useQuery({
    queryKey: ['feeds'],
    queryFn: async () => {
      const response = await getRSSFeeds();
      return response.data.data || [];
    },
    retry: 1,
  });

  const articles: Article[] = articlesData || [];
  const feedCount = feedsData?.length || 0;

  // Filter articles for today
  const todayArticles = articles.filter(a => {
    const articleDate = new Date(a.published_at || a.published || '');
    const today = new Date();
    return articleDate.toDateString() === today.toDateString();
  });

  const recentArticles = articles.slice(0, 6);
  const featuredArticles = articles.slice(0, 3);

  const [refreshing, setRefreshing] = React.useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetchArticles();
    setRefreshing(false);
  };

  const handleNavigateToChat = () => {
    navigation.navigate('Chat');
  };

  const handleNavigateToFeeds = () => {
    navigation.navigate('Feeds');
  };

  return (
    <View style={[styles.container, {backgroundColor: theme.colors.background}]}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={theme.colors.primary}
          />
        }>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <LinearGradient
              colors={[theme.colors.primary, theme.colors.accent]}
              start={{x: 0, y: 0}}
              end={{x: 1, y: 1}}
              style={[
                styles.headerIcon,
                {borderRadius: theme.borderRadius.xl},
              ]}>
              <Newspaper size={24} color="#FFFFFF" />
            </LinearGradient>
            <View>
              <Text
                style={[
                  styles.headerTitle,
                  {
                    color: theme.colors.textPrimary,
                    fontSize: theme.typography.fontSize['3xl'],
                    fontWeight: theme.typography.fontWeight.bold,
                  },
                ]}>
                Dashboard
              </Text>
              <Text
                style={[
                  styles.headerSubtitle,
                  {
                    color: theme.colors.textSecondary,
                    fontSize: theme.typography.fontSize.sm,
                  },
                ]}>
                Your personalized news
              </Text>
            </View>
          </View>
        </View>

        {/* Stats Cards */}
        <View style={styles.statsGrid}>
          {/* Total Articles */}
          <GlassCard style={styles.statCard}>
            <View style={styles.statContent}>
              <View
                style={[
                  styles.statIcon,
                  {
                    backgroundColor: theme.colors.primary + '20',
                    borderRadius: theme.borderRadius.lg,
                  },
                ]}>
                <Newspaper size={24} color={theme.colors.primary} />
              </View>
              <View style={styles.statText}>
                <Text
                  style={[
                    styles.statValue,
                    {
                      color: theme.colors.textPrimary,
                      fontSize: theme.typography.fontSize['2xl'],
                      fontWeight: theme.typography.fontWeight.bold,
                    },
                  ]}>
                  {articles.length}
                </Text>
                <Text
                  style={[
                    styles.statLabel,
                    {
                      color: theme.colors.textSecondary,
                      fontSize: theme.typography.fontSize.sm,
                    },
                  ]}>
                  Total Articles
                </Text>
              </View>
            </View>
          </GlassCard>

          {/* Active Feeds */}
          <GlassCard style={styles.statCard}>
            <View style={styles.statContent}>
              <View
                style={[
                  styles.statIcon,
                  {
                    backgroundColor: theme.colors.accent + '20',
                    borderRadius: theme.borderRadius.lg,
                  },
                ]}>
                <Rss size={24} color={theme.colors.accent} />
              </View>
              <View style={styles.statText}>
                <Text
                  style={[
                    styles.statValue,
                    {
                      color: theme.colors.textPrimary,
                      fontSize: theme.typography.fontSize['2xl'],
                      fontWeight: theme.typography.fontWeight.bold,
                    },
                  ]}>
                  {feedCount}
                </Text>
                <Text
                  style={[
                    styles.statLabel,
                    {
                      color: theme.colors.textSecondary,
                      fontSize: theme.typography.fontSize.sm,
                    },
                  ]}>
                  Active Feeds
                </Text>
              </View>
            </View>
          </GlassCard>

          {/* New Today */}
          <GlassCard style={styles.statCard}>
            <View style={styles.statContent}>
              <View
                style={[
                  styles.statIcon,
                  {
                    backgroundColor: theme.colors.success + '20',
                    borderRadius: theme.borderRadius.lg,
                  },
                ]}>
                <Clock size={24} color={theme.colors.success} />
              </View>
              <View style={styles.statText}>
                <Text
                  style={[
                    styles.statValue,
                    {
                      color: theme.colors.textPrimary,
                      fontSize: theme.typography.fontSize['2xl'],
                      fontWeight: theme.typography.fontWeight.bold,
                    },
                  ]}>
                  {todayArticles.length}
                </Text>
                <Text
                  style={[
                    styles.statLabel,
                    {
                      color: theme.colors.textSecondary,
                      fontSize: theme.typography.fontSize.sm,
                    },
                  ]}>
                  New Today
                </Text>
              </View>
            </View>
          </GlassCard>

          {/* Ask AI */}
          <GlassCard pressable onPress={handleNavigateToChat} style={styles.statCard}>
            <View style={styles.statContent}>
              <View
                style={[
                  styles.statIcon,
                  {
                    backgroundColor: '#A855F7' + '20',
                    borderRadius: theme.borderRadius.lg,
                  },
                ]}>
                <MessageSquare size={24} color="#A855F7" />
              </View>
              <View style={styles.statText}>
                <Text
                  style={[
                    styles.statValue,
                    {
                      color: theme.colors.textPrimary,
                      fontSize: theme.typography.fontSize.lg,
                      fontWeight: theme.typography.fontWeight.semibold,
                    },
                  ]}>
                  Ask AI
                </Text>
                <Text
                  style={[
                    styles.statLabel,
                    {
                      color: theme.colors.textSecondary,
                      fontSize: theme.typography.fontSize.sm,
                    },
                  ]}>
                  About your news
                </Text>
              </View>
            </View>
          </GlassCard>
        </View>

        {/* Loading State */}
        {articlesLoading && (
          <View style={styles.section}>
            <Skeleton height={200} style={{marginBottom: 16}} />
            <Skeleton height={200} style={{marginBottom: 16}} />
            <Skeleton height={200} />
          </View>
        )}

        {/* Empty State */}
        {!articlesLoading && articles.length === 0 && (
          <GlassCard style={styles.emptyCard}>
            <View style={styles.emptyContent}>
              <View
                style={[
                  styles.emptyIcon,
                  {
                    backgroundColor: theme.colors.muted,
                    borderRadius: theme.borderRadius.full,
                  },
                ]}>
                <Newspaper size={40} color={theme.colors.textSecondary} />
              </View>
              <Text
                style={[
                  styles.emptyTitle,
                  {
                    color: theme.colors.textPrimary,
                    fontSize: theme.typography.fontSize.xl,
                    fontWeight: theme.typography.fontWeight.semibold,
                  },
                ]}>
                No articles yet
              </Text>
              <Text
                style={[
                  styles.emptyText,
                  {
                    color: theme.colors.textSecondary,
                    fontSize: theme.typography.fontSize.base,
                  },
                ]}>
                Get started by adding RSS feeds to curate your personalized news digest.
              </Text>
              <GlassButton
                onPress={handleNavigateToFeeds}
                icon={<Rss size={18} color="#FFFFFF" />}
                iconPosition="left"
                style={{marginTop: 16}}>
                Add Your First Feed
              </GlassButton>
            </View>
          </GlassCard>
        )}

        {/* Featured Articles */}
        {!articlesLoading && featuredArticles.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <TrendingUp size={20} color={theme.colors.primary} />
              <Text
                style={[
                  styles.sectionTitle,
                  {
                    color: theme.colors.textPrimary,
                    fontSize: theme.typography.fontSize.xl,
                    fontWeight: theme.typography.fontWeight.semibold,
                  },
                ]}>
                Featured Stories
              </Text>
            </View>
            {featuredArticles.map((article, index) => (
              <View key={article.id || index} style={{marginBottom: 12}}>
                <ArticleCard article={article} />
              </View>
            ))}
          </View>
        )}

        {/* Recent Articles */}
        {!articlesLoading && recentArticles.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Clock size={20} color={theme.colors.primary} />
              <Text
                style={[
                  styles.sectionTitle,
                  {
                    color: theme.colors.textPrimary,
                    fontSize: theme.typography.fontSize.xl,
                    fontWeight: theme.typography.fontWeight.semibold,
                  },
                ]}>
                Recent Articles
              </Text>
            </View>
            {articles.length > 6 && (
              <Text
                style={[
                  styles.sectionCount,
                  {
                    color: theme.colors.textSecondary,
                    fontSize: theme.typography.fontSize.sm,
                  },
                ]}>
                Showing {recentArticles.length} of {articles.length}
              </Text>
            )}
            {recentArticles.map((article, index) => (
              <View key={article.id || index} style={{marginBottom: 12}}>
                <ArticleCard article={article} />
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
    paddingBottom: 40,
  },
  header: {
    marginBottom: 24,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  headerIcon: {
    width: 48,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    marginBottom: 2,
  },
  headerSubtitle: {},
  statsGrid: {
    gap: 12,
    marginBottom: 24,
  },
  statCard: {
    marginBottom: 0,
  },
  statContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  statIcon: {
    width: 48,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statText: {
    flex: 1,
  },
  statValue: {
    marginBottom: 2,
  },
  statLabel: {},
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
  },
  sectionTitle: {},
  sectionCount: {
    marginBottom: 12,
  },
  emptyCard: {
    padding: 32,
  },
  emptyContent: {
    alignItems: 'center',
  },
  emptyIcon: {
    width: 80,
    height: 80,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  emptyTitle: {
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyText: {
    textAlign: 'center',
    lineHeight: 24,
  },
});
