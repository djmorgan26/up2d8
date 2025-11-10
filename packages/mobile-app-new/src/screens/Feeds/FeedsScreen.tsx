/**
 * Feeds Screen
 * RSS feed management - add, view, delete feeds
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  Alert,
} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {GlassCard, GlassButton, Input, Badge, Skeleton} from '@components/ui';
import {useQuery, useMutation, useQueryClient} from '@tanstack/react-query';
import {getRSSFeeds, addRSSFeed, deleteRSSFeed} from '@up2d8/shared-api';
import {Feed} from '@up2d8/shared-types';
import {Rss, Plus, Trash2, ExternalLink} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';
import {Linking} from 'react-native';

export default function FeedsScreen() {
  const {theme} = useTheme();
  const queryClient = useQueryClient();
  const [showAddFeed, setShowAddFeed] = useState(false);
  const [newFeedUrl, setNewFeedUrl] = useState('');
  const [newFeedTitle, setNewFeedTitle] = useState('');

  // Fetch feeds
  const {
    data: feedsData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['feeds'],
    queryFn: async () => {
      const response = await getRSSFeeds();
      return response.data.data || [];
    },
    retry: 1,
  });

  const feeds: Feed[] = feedsData || [];

  // Add feed mutation
  const addFeedMutation = useMutation({
    mutationFn: async () => {
      return await addRSSFeed(newFeedUrl, undefined, newFeedTitle);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({queryKey: ['feeds']});
      queryClient.invalidateQueries({queryKey: ['articles']});
      setNewFeedUrl('');
      setNewFeedTitle('');
      setShowAddFeed(false);
      Alert.alert('Success', 'Feed added successfully');
    },
    onError: (error: any) => {
      Alert.alert('Error', error.message || 'Failed to add feed');
    },
  });

  // Delete feed mutation
  const deleteFeedMutation = useMutation({
    mutationFn: async (feedId: string) => {
      return await deleteRSSFeed(feedId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({queryKey: ['feeds']});
      queryClient.invalidateQueries({queryKey: ['articles']});
      Alert.alert('Success', 'Feed deleted successfully');
    },
    onError: (error: any) => {
      Alert.alert('Error', error.message || 'Failed to delete feed');
    },
  });

  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const handleAddFeed = () => {
    if (!newFeedUrl.trim()) {
      Alert.alert('Error', 'Please enter a feed URL');
      return;
    }
    addFeedMutation.mutate();
  };

  const handleDeleteFeed = (feedId: string, feedTitle?: string) => {
    Alert.alert(
      'Delete Feed',
      `Are you sure you want to delete ${feedTitle || 'this feed'}?`,
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => deleteFeedMutation.mutate(feedId),
        },
      ],
    );
  };

  const handleOpenFeedUrl = async (url: string) => {
    const canOpen = await Linking.canOpenURL(url);
    if (canOpen) {
      await Linking.openURL(url);
    }
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
              <Rss size={24} color="#FFFFFF" />
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
                Feeds
              </Text>
              <Text
                style={[
                  styles.headerSubtitle,
                  {
                    color: theme.colors.textSecondary,
                    fontSize: theme.typography.fontSize.sm,
                  },
                ]}>
                {feeds.length} active {feeds.length === 1 ? 'feed' : 'feeds'}
              </Text>
            </View>
          </View>
        </View>

        {/* Add Feed Button */}
        <GlassButton
          onPress={() => setShowAddFeed(!showAddFeed)}
          icon={<Plus size={20} color="#FFFFFF" />}
          iconPosition="left"
          style={{marginBottom: 16}}>
          {showAddFeed ? 'Cancel' : 'Add Feed'}
        </GlassButton>

        {/* Add Feed Form */}
        {showAddFeed && (
          <GlassCard style={{marginBottom: 16}}>
            <Text
              style={[
                styles.formTitle,
                {
                  color: theme.colors.textPrimary,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.semibold,
                },
              ]}>
              Add RSS Feed
            </Text>
            <Input
              label="Feed URL"
              placeholder="https://example.com/feed.xml"
              value={newFeedUrl}
              onChangeText={setNewFeedUrl}
              keyboardType="url"
              autoCapitalize="none"
              autoCorrect={false}
            />
            <Input
              label="Title (optional)"
              placeholder="Feed name"
              value={newFeedTitle}
              onChangeText={setNewFeedTitle}
            />
            <GlassButton
              onPress={handleAddFeed}
              loading={addFeedMutation.isPending}
              disabled={!newFeedUrl.trim()}>
              Add Feed
            </GlassButton>
          </GlassCard>
        )}

        {/* Loading State */}
        {isLoading && (
          <View>
            <Skeleton height={100} style={{marginBottom: 12}} />
            <Skeleton height={100} style={{marginBottom: 12}} />
            <Skeleton height={100} />
          </View>
        )}

        {/* Empty State */}
        {!isLoading && feeds.length === 0 && (
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
                <Rss size={40} color={theme.colors.textSecondary} />
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
                No feeds yet
              </Text>
              <Text
                style={[
                  styles.emptyText,
                  {
                    color: theme.colors.textSecondary,
                    fontSize: theme.typography.fontSize.base,
                  },
                ]}>
                Add your first RSS feed to start reading personalized news.
              </Text>
            </View>
          </GlassCard>
        )}

        {/* Feeds List */}
        {!isLoading &&
          feeds.map((feed, index) => (
            <GlassCard
              key={feed.id || index}
              style={{marginBottom: 12}}
              pressable
              onPress={() => handleOpenFeedUrl(feed.url)}>
              <View style={styles.feedCard}>
                <View style={styles.feedHeader}>
                  <View style={styles.feedIcon}>
                    <Rss size={20} color={theme.colors.primary} />
                  </View>
                  <View style={styles.feedInfo}>
                    <Text
                      style={[
                        styles.feedTitle,
                        {
                          color: theme.colors.textPrimary,
                          fontSize: theme.typography.fontSize.base,
                          fontWeight: theme.typography.fontWeight.semibold,
                        },
                      ]}
                      numberOfLines={1}>
                      {feed.title || 'Untitled Feed'}
                    </Text>
                    <Text
                      style={[
                        styles.feedUrl,
                        {
                          color: theme.colors.textSecondary,
                          fontSize: theme.typography.fontSize.sm,
                        },
                      ]}
                      numberOfLines={1}>
                      {feed.url}
                    </Text>
                  </View>
                </View>

                <View style={styles.feedFooter}>
                  {feed.category && (
                    <Badge variant="primary">{feed.category}</Badge>
                  )}
                  <GlassButton
                    variant="destructive"
                    size="sm"
                    onPress={() => handleDeleteFeed(feed.id, feed.title)}
                    icon={<Trash2 size={14} color="#FFFFFF" />}
                    loading={deleteFeedMutation.isPending}>
                    Delete
                  </GlassButton>
                </View>
              </View>
            </GlassCard>
          ))}
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
  formTitle: {
    marginBottom: 16,
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
  feedCard: {
    padding: 0,
  },
  feedHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  feedIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(65, 105, 225, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  feedInfo: {
    flex: 1,
  },
  feedTitle: {
    marginBottom: 2,
  },
  feedUrl: {},
  feedFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
});
