import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Animated,
  ActivityIndicator,
  Linking,
  Alert,
  RefreshControl,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import Icon from 'react-native-vector-icons/Ionicons';
import { GlassCard } from '../components/GlassCard';
import {
  getAllArticles,
  getRelativeTime,
  sortArticlesByDate,
} from '../services/articlesService';
import { isUsingMockData } from '../services/api';
import { triggerHaptic } from '../utils/haptics';
import {
  colors,
  spacing,
  typography,
  borderRadius,
} from '../theme/tokens';
import LinearGradient from 'react-native-linear-gradient';
import { Article } from '../types';

const ArticleCard = ({ article, theme, onPress }) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.98,
      useNativeDriver: true,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
    }).start();
  };

  return (
    <TouchableOpacity
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      onPress={onPress}
      activeOpacity={0.9}
    >
      <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
        <GlassCard style={styles.articleCard}>
          <Text style={[styles.articleTitle, { color: theme.colors.textPrimary }]}>
            {article.title}
          </Text>

          <Text
            style={[styles.articleSummary, { color: theme.colors.textSecondary }]}
            numberOfLines={3}
          >
            {article.summary}
          </Text>

          <View style={styles.articleFooter}>
            <View style={styles.tagsContainer}>
              {article.tags.slice(0, 3).map((tag, index) => (
                <View
                  key={index}
                  style={[
                    styles.tag,
                    { backgroundColor: `${theme.colors.primary}20` },
                  ]}
                >
                  <Text style={[styles.tagText, { color: theme.colors.primary }]}>
                    {tag}
                  </Text>
                </View>
              ))}
            </View>

            <Text style={[styles.timestamp, { color: theme.colors.textTertiary }]}>
              {getRelativeTime(article.published)}
            </Text>
          </View>
        </GlassCard>
      </Animated.View>
    </TouchableOpacity>
  );
};

const BrowsePage: React.FC = () => {
  const { theme } = useTheme();
  const [articles, setArticles] = useState<Article[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const loadArticles = async () => {
    try {
      setIsLoading(true);
      const fetchedArticles = await getAllArticles();
      const sortedArticles = sortArticlesByDate(fetchedArticles);
      setArticles(sortedArticles);
    } catch (error) {
      console.error('Error loading articles:', error);
      Alert.alert(
        'Error',
        'Failed to load articles. Showing demo data.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    triggerHaptic('light');
    await loadArticles();
    setIsRefreshing(false);
    triggerHaptic('success');
  };

  useEffect(() => {
    loadArticles();
  }, []);

  const handleArticlePress = async (article: Article) => {
    triggerHaptic('light');

    const canOpen = await Linking.canOpenURL(article.link);
    if (canOpen) {
      await Linking.openURL(article.link);
    } else {
      Alert.alert('Error', 'Cannot open article link');
    }
  };

  const handleCategoryPress = (category: string) => {
    triggerHaptic('light');
    setSelectedCategory(category === selectedCategory ? null : category);
  };

  // Get all unique tags from articles
  const allTags = Array.from(
    new Set(articles.flatMap(article => article.tags))
  );

  // Filter articles by selected category
  const filteredArticles = selectedCategory
    ? articles.filter(article => article.tags.includes(selectedCategory))
    : articles;

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <LinearGradient
        colors={[theme.colors.accent, theme.colors.background]}
        style={styles.gradientContainer}
      />

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={handleRefresh}
            tintColor={theme.colors.primary}
          />
        }
      >
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.colors.textPrimary }]}>
            Discover
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            {isUsingMockData()
              ? '🔴 Demo Mode - Connect backend for live news'
              : `${articles.length} articles available`}
          </Text>
        </View>

        {/* Categories */}
        {allTags.length > 0 && (
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.categoriesScroll}
            contentContainerStyle={styles.categoriesContent}
          >
            {allTags.map((tag, index) => (
              <TouchableOpacity
                key={index}
                onPress={() => handleCategoryPress(tag)}
              >
                <View
                  style={[
                    styles.categoryChip,
                    {
                      backgroundColor:
                        selectedCategory === tag
                          ? theme.colors.primary
                          : `${theme.colors.surface}80`,
                    },
                  ]}
                >
                  <Text
                    style={[
                      styles.categoryText,
                      {
                        color:
                          selectedCategory === tag
                            ? 'white'
                            : theme.colors.textPrimary,
                      },
                    ]}
                  >
                    {tag}
                  </Text>
                </View>
              </TouchableOpacity>
            ))}
          </ScrollView>
        )}

        {/* Articles */}
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={theme.colors.primary} />
            <Text style={[styles.loadingText, { color: theme.colors.textSecondary }]}>
              Loading articles...
            </Text>
          </View>
        ) : filteredArticles.length > 0 ? (
          <>
            {selectedCategory && (
              <Text
                style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}
              >
                {selectedCategory} ({filteredArticles.length})
              </Text>
            )}
            {filteredArticles.map((article) => (
              <ArticleCard
                key={article.id}
                article={article}
                theme={theme}
                onPress={() => handleArticlePress(article)}
              />
            ))}
          </>
        ) : (
          <GlassCard style={styles.emptyCard}>
            <Icon name="newspaper-outline" size={48} color={theme.colors.textTertiary} />
            <Text style={[styles.emptyText, { color: theme.colors.textSecondary }]}>
              No articles available
            </Text>
            <Text style={[styles.emptySubtext, { color: theme.colors.textTertiary }]}>
              Pull down to refresh
            </Text>
          </GlassCard>
        )}
      </ScrollView>
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
    borderBottomLeftRadius: borderRadius['3xl'],
    borderBottomRightRadius: borderRadius['3xl'],
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: spacing[4],
    paddingBottom: spacing[24],
  },
  header: {
    marginTop: spacing[8],
    marginBottom: spacing[4],
  },
  title: {
    fontSize: typography.fontSize['4xl'],
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[2],
  },
  subtitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.regular as any,
  },
  categoriesScroll: {
    marginBottom: spacing[4],
  },
  categoriesContent: {
    paddingRight: spacing[4],
  },
  categoryChip: {
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[2],
    borderRadius: borderRadius.full,
    marginRight: spacing[2],
  },
  categoryText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold as any,
  },
  sectionTitle: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[4],
  },
  articleCard: {
    marginBottom: spacing[4],
    padding: spacing[4],
  },
  articleTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[2],
    lineHeight: typography.lineHeight.snug * typography.fontSize.lg,
  },
  articleSummary: {
    fontSize: typography.fontSize.sm,
    lineHeight: typography.lineHeight.relaxed * typography.fontSize.sm,
    marginBottom: spacing[3],
  },
  articleFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    flex: 1,
  },
  tag: {
    paddingHorizontal: spacing[2],
    paddingVertical: spacing[1],
    borderRadius: borderRadius.sm,
    marginRight: spacing[1],
    marginBottom: spacing[1],
  },
  tagText: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.medium as any,
  },
  timestamp: {
    fontSize: typography.fontSize.xs,
    marginLeft: spacing[2],
  },
  loadingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing[12],
  },
  loadingText: {
    marginTop: spacing[4],
    fontSize: typography.fontSize.base,
  },
  emptyCard: {
    alignItems: 'center',
    paddingVertical: spacing[12],
  },
  emptyText: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semibold as any,
    marginTop: spacing[4],
  },
  emptySubtext: {
    fontSize: typography.fontSize.sm,
    marginTop: spacing[2],
  },
});

export default BrowsePage;
