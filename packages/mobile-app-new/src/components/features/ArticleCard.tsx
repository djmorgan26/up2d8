/**
 * ArticleCard Component
 * Article preview card for dashboard and browse
 */

import React from 'react';
import {View, Text, StyleSheet, Pressable, Linking, Alert} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {GlassCard} from '@components/ui';
import {Article} from '@up2d8/shared-types';
import {getRelativeTime} from '@up2d8/shared-utils';
import {ExternalLink, Calendar} from 'lucide-react-native';

interface ArticleCardProps {
  article: Article;
}

export function ArticleCard({article}: ArticleCardProps) {
  const {theme} = useTheme();

  const handlePress = async () => {
    const url = article.url || article.link;
    if (!url) {
      Alert.alert('Error', 'No article URL available');
      return;
    }

    const canOpen = await Linking.canOpenURL(url);
    if (canOpen) {
      await Linking.openURL(url);
    } else {
      Alert.alert('Error', 'Cannot open article link');
    }
  };

  const publishedDate = article.published_at || article.published;
  const description = article.description || article.summary;

  return (
    <GlassCard pressable onPress={handlePress}>
      <View style={styles.content}>
        {/* Title */}
        <Text
          style={[
            styles.title,
            {
              color: theme.colors.textPrimary,
              fontSize: theme.typography.fontSize.lg,
              fontWeight: theme.typography.fontWeight.bold,
            },
          ]}
          numberOfLines={3}>
          {article.title}
        </Text>

        {/* Description */}
        {description && (
          <Text
            style={[
              styles.description,
              {
                color: theme.colors.textSecondary,
                fontSize: theme.typography.fontSize.sm,
              },
            ]}
            numberOfLines={3}>
            {description}
          </Text>
        )}

        {/* Footer */}
        <View style={styles.footer}>
          <View style={styles.meta}>
            {/* Source */}
            {article.source && (
              <Text
                style={[
                  styles.source,
                  {
                    color: theme.colors.primary,
                    fontSize: theme.typography.fontSize.xs,
                    fontWeight: theme.typography.fontWeight.semibold,
                  },
                ]}>
                {article.source}
              </Text>
            )}

            {/* Date */}
            {publishedDate && (
              <View style={styles.dateContainer}>
                <Calendar size={12} color={theme.colors.textTertiary} />
                <Text
                  style={[
                    styles.date,
                    {
                      color: theme.colors.textTertiary,
                      fontSize: theme.typography.fontSize.xs,
                    },
                  ]}>
                  {getRelativeTime(publishedDate)}
                </Text>
              </View>
            )}
          </View>

          <ExternalLink size={16} color={theme.colors.textSecondary} />
        </View>
      </View>
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  content: {
    padding: 0, // GlassCard already has padding
  },
  title: {
    marginBottom: 8,
    lineHeight: 24,
  },
  description: {
    marginBottom: 12,
    lineHeight: 20,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  meta: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  source: {
    textTransform: 'uppercase',
  },
  dateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  date: {},
});
