import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { ArticleCard } from '../components/ArticleCard';
import { GlassCard } from '../components/GlassCard';
import Icon from 'react-native-vector-icons/Ionicons';
import LinearGradient from 'react-native-linear-gradient';
import { colors, spacing, typography, borderRadius } from '../theme/tokens';
import { useArticlesStore } from '../store/articlesStore';
import { useUserStore } from '../store/userStore';

const DigestScreen: React.FC = () => {
  const { theme } = useTheme();
  const { articles, isLoading, fetchPersonalizedArticles, filterByTopics } = useArticlesStore();
  const { topics } = useUserStore();
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    // Load articles on mount
    if (topics && topics.length > 0) {
      loadArticles();
    }
  }, [topics]);

  const loadArticles = async () => {
    try {
      if (topics && topics.length > 0) {
        await fetchPersonalizedArticles(topics);
      }
    } catch (error) {
      console.error('Error loading articles:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadArticles();
    setRefreshing(false);
  };

  const renderHeader = () => (
    <View style={styles.headerContent}>
      {/* Date */}
      <Text style={[styles.date, { color: theme.colors.textSecondary }]}>
        {new Date().toLocaleDateString('en-US', {
          weekday: 'long',
          month: 'long',
          day: 'numeric',
        })}
      </Text>

      {/* Topics */}
      {topics && topics.length > 0 && (
        <View style={styles.topicsSection}>
          <Text style={[styles.topicsLabel, { color: theme.colors.textSecondary }]}>
            Your interests:
          </Text>
          <View style={styles.topicsContainer}>
            {topics.map((topic, index) => (
              <View
                key={index}
                style={[
                  styles.topicPill,
                  {
                    backgroundColor: theme.colors.primary + '20',
                    borderColor: theme.colors.primary,
                  },
                ]}
              >
                <Text style={[styles.topicText, { color: theme.colors.primary }]}>
                  {topic}
                </Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Article count */}
      {articles.length > 0 && (
        <Text style={[styles.articleCount, { color: theme.colors.textSecondary }]}>
          {articles.length} {articles.length === 1 ? 'article' : 'articles'} for you
        </Text>
      )}
    </View>
  );

  const renderEmpty = () => {
    if (isLoading) {
      return (
        <View style={styles.emptyContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <Text style={[styles.emptyText, { color: theme.colors.textSecondary }]}>
            Loading your personalized digest...
          </Text>
        </View>
      );
    }

    if (!topics || topics.length === 0) {
      return (
        <View style={styles.emptyContainer}>
          <GlassCard style={styles.emptyCard}>
            <Icon
              name="newspaper-outline"
              size={64}
              color={theme.colors.textSecondary}
            />
            <Text style={[styles.emptyTitle, { color: theme.colors.textPrimary }]}>
              No Topics Selected
            </Text>
            <Text style={[styles.emptyText, { color: theme.colors.textSecondary }]}>
              Go to your Profile to select topics you're interested in
            </Text>
          </GlassCard>
        </View>
      );
    }

    return (
      <View style={styles.emptyContainer}>
        <GlassCard style={styles.emptyCard}>
          <Icon
            name="cafe-outline"
            size={64}
            color={theme.colors.textSecondary}
          />
          <Text style={[styles.emptyTitle, { color: theme.colors.textPrimary }]}>
            No Articles Yet
          </Text>
          <Text style={[styles.emptyText, { color: theme.colors.textSecondary }]}>
            We're working on gathering articles for your topics. Check back soon!
          </Text>
          <TouchableOpacity onPress={handleRefresh} style={styles.refreshButton}>
            <Text style={[styles.refreshText, { color: theme.colors.primary }]}>
              Refresh
            </Text>
          </TouchableOpacity>
        </GlassCard>
      </View>
    );
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <LinearGradient
        colors={[theme.colors.accent, theme.colors.background]}
        style={styles.gradientContainer}
      />

      {/* Header */}
      <View style={[styles.header, { backgroundColor: theme.colors.background }]}>
        <View>
          <Text style={[styles.title, { color: theme.colors.textPrimary }]}>
            Your Digest
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            Personalized news just for you
          </Text>
        </View>
      </View>

      {/* Articles List */}
      <FlatList
        data={articles}
        renderItem={({ item }) => <ArticleCard article={item} />}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        ListHeaderComponent={articles.length > 0 ? renderHeader() : null}
        ListEmptyComponent={renderEmpty()}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={theme.colors.primary}
          />
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradientContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 300,
    opacity: 0.1,
  },
  header: {
    paddingTop: spacing[12],
    paddingHorizontal: spacing[4],
    paddingBottom: spacing[4],
  },
  title: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.bold as any,
  },
  subtitle: {
    fontSize: typography.fontSize.sm,
    marginTop: spacing[1],
  },
  listContent: {
    paddingHorizontal: spacing[4],
    paddingBottom: spacing[12],
  },
  headerContent: {
    marginBottom: spacing[4],
  },
  date: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.medium as any,
    marginBottom: spacing[4],
  },
  topicsSection: {
    marginBottom: spacing[4],
  },
  topicsLabel: {
    fontSize: typography.fontSize.sm,
    marginBottom: spacing[2],
  },
  topicsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  topicPill: {
    paddingHorizontal: spacing[3],
    paddingVertical: spacing[1],
    borderRadius: borderRadius.full,
    marginRight: spacing[2],
    marginBottom: spacing[2],
    borderWidth: 1,
  },
  topicText: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.semibold as any,
  },
  articleCount: {
    fontSize: typography.fontSize.sm,
    marginBottom: spacing[2],
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing[6],
    paddingTop: spacing[12],
  },
  emptyCard: {
    alignItems: 'center',
    padding: spacing[8],
  },
  emptyTitle: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold as any,
    marginTop: spacing[4],
    marginBottom: spacing[2],
    textAlign: 'center',
  },
  emptyText: {
    fontSize: typography.fontSize.base,
    textAlign: 'center',
    lineHeight: typography.fontSize.base * 1.5,
  },
  refreshButton: {
    marginTop: spacing[4],
    paddingVertical: spacing[2],
    paddingHorizontal: spacing[4],
  },
  refreshText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold as any,
  },
});

export default DigestScreen;
