import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Linking } from 'react-native';
import { GlassCard } from './GlassCard';
import Icon from 'react-native-vector-icons/Ionicons';
import { colors, spacing, typography, borderRadius } from '../theme/tokens';
import { useTheme } from '../context/ThemeContext';
import { Article } from '../types';
import { getRelativeTime } from '../services/articlesService';

interface ArticleCardProps {
  article: Article;
  onPress?: () => void;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({ article, onPress }) => {
  const { theme } = useTheme();

  const handlePress = () => {
    if (onPress) {
      onPress();
    } else {
      // Default: Open in browser
      Linking.openURL(article.link).catch((err) =>
        console.error('Failed to open URL:', err)
      );
    }
  };

  const getTagColor = (index: number) => {
    const colorOptions = [
      colors.primary[500],
      colors.accent[500],
      colors.primary[600],
      colors.accent[600],
    ];
    return colorOptions[index % colorOptions.length];
  };

  return (
    <TouchableOpacity onPress={handlePress} activeOpacity={0.7}>
      <GlassCard style={styles.card}>
        {/* Tags */}
        {article.tags && article.tags.length > 0 && (
          <View style={styles.tagsContainer}>
            {article.tags.slice(0, 3).map((tag, index) => (
              <View
                key={index}
                style={[
                  styles.tag,
                  { backgroundColor: getTagColor(index) + '20' },
                ]}
              >
                <Text
                  style={[styles.tagText, { color: getTagColor(index) }]}
                >
                  {tag}
                </Text>
              </View>
            ))}
          </View>
        )}

        {/* Title */}
        <Text
          style={[styles.title, { color: theme.colors.textPrimary }]}
          numberOfLines={3}
        >
          {article.title}
        </Text>

        {/* Summary */}
        {article.summary && (
          <Text
            style={[styles.summary, { color: theme.colors.textSecondary }]}
            numberOfLines={3}
          >
            {article.summary}
          </Text>
        )}

        {/* Footer */}
        <View style={styles.footer}>
          <View style={styles.metaInfo}>
            <Icon
              name="time-outline"
              size={14}
              color={theme.colors.textSecondary}
            />
            <Text style={[styles.metaText, { color: theme.colors.textSecondary }]}>
              {getRelativeTime(article.published)}
            </Text>
          </View>
          <View style={styles.readMore}>
            <Text style={[styles.readMoreText, { color: theme.colors.primary }]}>
              Read more
            </Text>
            <Icon name="arrow-forward" size={14} color={theme.colors.primary} />
          </View>
        </View>
      </GlassCard>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    padding: spacing[4],
    marginBottom: spacing[4],
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: spacing[3],
  },
  tag: {
    paddingHorizontal: spacing[2],
    paddingVertical: spacing[1],
    borderRadius: borderRadius.sm,
    marginRight: spacing[2],
    marginBottom: spacing[1],
  },
  tagText: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.semibold as any,
  },
  title: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[2],
    lineHeight: typography.fontSize.lg * 1.4,
  },
  summary: {
    fontSize: typography.fontSize.sm,
    lineHeight: typography.fontSize.sm * 1.5,
    marginBottom: spacing[3],
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  metaInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaText: {
    fontSize: typography.fontSize.xs,
    marginLeft: spacing[1],
  },
  readMore: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  readMoreText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold as any,
    marginRight: spacing[1],
  },
});
