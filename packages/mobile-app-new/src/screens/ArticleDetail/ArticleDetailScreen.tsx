/**
 * Article Detail Screen
 * Full article view with content, metadata, and actions
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Linking,
  Share,
  Alert,
} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {GlassCard, GlassButton} from '@components/ui';
import {Article} from '@up2d8/shared-types';
import {getRelativeTime} from '@up2d8/shared-utils';
import {
  ExternalLink,
  Share2,
  Calendar,
  Tag,
  ArrowLeft,
} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {HomeStackParamList} from '@navigation/types';

type Props = NativeStackScreenProps<HomeStackParamList, 'ArticleDetail'>;

export default function ArticleDetailScreen({route, navigation}: Props) {
  const {article} = route.params;
  const {theme} = useTheme();
  const [isSharing, setIsSharing] = useState(false);

  const handleOpenUrl = async () => {
    const url = article.url || article.link;
    if (!url) {
      Alert.alert('Error', 'No URL available for this article');
      return;
    }

    try {
      const canOpen = await Linking.canOpenURL(url);
      if (canOpen) {
        await Linking.openURL(url);
      } else {
        Alert.alert('Error', 'Cannot open this URL');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to open URL');
    }
  };

  const handleShare = async () => {
    const url = article.url || article.link;
    if (!url) {
      Alert.alert('Error', 'No URL available to share');
      return;
    }

    setIsSharing(true);
    try {
      await Share.share({
        message: `${article.title}\n\n${url}`,
        url: url,
        title: article.title,
      });
    } catch (error) {
      // User cancelled or error occurred
    } finally {
      setIsSharing(false);
    }
  };

  const description =
    article.description ||
    article.content?.substring(0, 300) + '...' ||
    'No description available';

  const publishedDate = article.published_at || article.published;

  return (
    <View style={[styles.container, {backgroundColor: theme.colors.background}]}>
      {/* Header */}
      <View
        style={[
          styles.header,
          {
            backgroundColor: theme.colors.card,
            borderBottomWidth: 1,
            borderBottomColor: theme.colors.border,
          },
        ]}>
        <GlassButton
          variant="ghost"
          size="icon"
          onPress={() => navigation.goBack()}
          icon={<ArrowLeft size={24} color={theme.colors.textPrimary} />}
        />
        <Text
          style={[
            styles.headerTitle,
            {
              color: theme.colors.textPrimary,
              fontSize: theme.typography.fontSize.lg,
              fontWeight: theme.typography.fontWeight.semibold,
            },
          ]}>
          Article
        </Text>
        <View style={{width: 40}} />
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}>
        {/* Title Section */}
        <GlassCard style={styles.titleCard}>
          <Text
            style={[
              styles.title,
              {
                color: theme.colors.textPrimary,
                fontSize: theme.typography.fontSize['2xl'],
                fontWeight: theme.typography.fontWeight.bold,
                lineHeight: theme.typography.fontSize['2xl'] * 1.3,
              },
            ]}>
            {article.title}
          </Text>

          {/* Metadata */}
          <View style={styles.metadata}>
            {article.source && (
              <View style={styles.metadataItem}>
                <View
                  style={[
                    styles.metadataIcon,
                    {backgroundColor: theme.colors.primary + '20'},
                  ]}>
                  <Tag size={14} color={theme.colors.primary} />
                </View>
                <Text
                  style={[
                    styles.metadataText,
                    {
                      color: theme.colors.textSecondary,
                      fontSize: theme.typography.fontSize.sm,
                    },
                  ]}>
                  {article.source}
                </Text>
              </View>
            )}

            {publishedDate && (
              <View style={styles.metadataItem}>
                <View
                  style={[
                    styles.metadataIcon,
                    {backgroundColor: theme.colors.accent + '20'},
                  ]}>
                  <Calendar size={14} color={theme.colors.accent} />
                </View>
                <Text
                  style={[
                    styles.metadataText,
                    {
                      color: theme.colors.textSecondary,
                      fontSize: theme.typography.fontSize.sm,
                    },
                  ]}>
                  {getRelativeTime(publishedDate)}
                </Text>
              </View>
            )}
          </View>
        </GlassCard>

        {/* Description/Content */}
        <GlassCard style={styles.contentCard}>
          <Text
            style={[
              styles.description,
              {
                color: theme.colors.textPrimary,
                fontSize: theme.typography.fontSize.base,
                lineHeight: theme.typography.fontSize.base * 1.6,
              },
            ]}>
            {description}
          </Text>

          {article.content && article.content.length > 300 && (
            <Text
              style={[
                styles.readMoreHint,
                {
                  color: theme.colors.textSecondary,
                  fontSize: theme.typography.fontSize.sm,
                  fontStyle: 'italic',
                },
              ]}>
              Tap "Read Full Article" below to continue reading...
            </Text>
          )}
        </GlassCard>

        {/* Actions */}
        <View style={styles.actions}>
          <GlassButton
            onPress={handleOpenUrl}
            icon={<ExternalLink size={20} color="#FFFFFF" />}
            iconPosition="left"
            style={styles.actionButton}>
            Read Full Article
          </GlassButton>

          <GlassButton
            variant="outline"
            onPress={handleShare}
            loading={isSharing}
            icon={<Share2 size={20} color={theme.colors.primary} />}
            iconPosition="left"
            style={styles.actionButton}>
            Share
          </GlassButton>
        </View>

        {/* Source Info */}
        {article.feed_id && (
          <GlassCard style={styles.sourceCard}>
            <Text
              style={[
                styles.sourceLabel,
                {
                  color: theme.colors.textSecondary,
                  fontSize: theme.typography.fontSize.xs,
                  fontWeight: theme.typography.fontWeight.medium,
                },
              ]}>
              FROM YOUR FEED
            </Text>
            <Text
              style={[
                styles.sourceName,
                {
                  color: theme.colors.textPrimary,
                  fontSize: theme.typography.fontSize.base,
                  fontWeight: theme.typography.fontWeight.semibold,
                },
              ]}>
              {article.source || 'Unknown Source'}
            </Text>
          </GlassCard>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 8,
    paddingVertical: 8,
    paddingTop: 50, // Account for status bar
  },
  headerTitle: {
    flex: 1,
    textAlign: 'center',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
    paddingBottom: 40,
  },
  titleCard: {
    marginBottom: 16,
  },
  title: {
    marginBottom: 16,
  },
  metadata: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  metadataItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  metadataIcon: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  metadataText: {},
  contentCard: {
    marginBottom: 16,
  },
  description: {
    marginBottom: 12,
  },
  readMoreHint: {
    marginTop: 8,
  },
  actions: {
    gap: 12,
    marginBottom: 16,
  },
  actionButton: {
    width: '100%',
  },
  sourceCard: {
    marginBottom: 16,
  },
  sourceLabel: {
    marginBottom: 4,
    letterSpacing: 1,
  },
  sourceName: {},
});
