import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { GlassCard } from '../components/GlassCard';
import { GlassButton } from '../components/GlassButton';
import Icon from 'react-native-vector-icons/Ionicons';
import LinearGradient from 'react-native-linear-gradient';
import { colors, spacing, typography, borderRadius } from '../theme/tokens';
import { useUserStore } from '../store/userStore';
import { AVAILABLE_TOPICS } from '../types';

const ProfileScreen: React.FC = () => {
  const { theme } = useTheme();
  const {
    email,
    topics,
    preferences,
    updateTopics,
    updatePreferences,
    unsubscribe,
    isLoading,
  } = useUserStore();

  const [isEditingTopics, setIsEditingTopics] = useState(false);
  const [selectedTopics, setSelectedTopics] = useState<string[]>(topics || []);

  const newsletterStyle = preferences?.newsletter_style || 'concise';

  const handleToggleTopic = (topic: string) => {
    if (selectedTopics.includes(topic)) {
      setSelectedTopics(selectedTopics.filter(t => t !== topic));
    } else {
      setSelectedTopics([...selectedTopics, topic]);
    }
  };

  const handleSaveTopics = async () => {
    if (selectedTopics.length === 0) {
      Alert.alert('No Topics', 'Please select at least one topic');
      return;
    }

    try {
      await updateTopics(selectedTopics);
      setIsEditingTopics(false);
      Alert.alert('Success', 'Your topics have been updated');
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to update topics');
    }
  };

  const handleCancelEditTopics = () => {
    setSelectedTopics(topics || []);
    setIsEditingTopics(false);
  };

  const handleToggleNewsletterStyle = async () => {
    const newStyle = newsletterStyle === 'concise' ? 'detailed' : 'concise';
    try {
      await updatePreferences(newStyle);
      Alert.alert('Success', `Newsletter style changed to ${newStyle}`);
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to update preferences');
    }
  };

  const handleUnsubscribe = () => {
    Alert.alert(
      'Unsubscribe',
      'Are you sure you want to unsubscribe from UP2D8? You will no longer receive daily digests.',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Unsubscribe',
          style: 'destructive',
          onPress: async () => {
            try {
              await unsubscribe();
              Alert.alert(
                'Unsubscribed',
                'You have been successfully unsubscribed. We hope to see you again!'
              );
            } catch (error: any) {
              Alert.alert('Error', error.message || 'Failed to unsubscribe');
            }
          },
        },
      ]
    );
  };

  const getTopicIcon = (topic: string): string => {
    const icons: { [key: string]: string } = {
      Technology: 'laptop-outline',
      AI: 'bulb-outline',
      Science: 'flask-outline',
      Business: 'briefcase-outline',
      Health: 'fitness-outline',
      Design: 'color-palette-outline',
      Education: 'school-outline',
      Politics: 'megaphone-outline',
      Environment: 'leaf-outline',
      Sports: 'football-outline',
    };
    return icons[topic] || 'star-outline';
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <LinearGradient
        colors={[colors.primary[700], theme.colors.background]}
        style={styles.gradientContainer}
      />

      {/* Header */}
      <View style={[styles.header, { backgroundColor: theme.colors.background }]}>
        <Text style={[styles.title, { color: theme.colors.textPrimary }]}>
          Profile & Settings
        </Text>
        <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
          Manage your subscription and preferences
        </Text>
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Account Info */}
        <GlassCard style={styles.section}>
          <View style={styles.sectionHeader}>
            <Icon name="person" size={24} color={theme.colors.primary} />
            <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>
              Account
            </Text>
          </View>
          <View style={styles.infoRow}>
            <Icon name="mail-outline" size={16} color={theme.colors.textSecondary} />
            <Text style={[styles.infoText, { color: theme.colors.textPrimary }]}>
              {email}
            </Text>
          </View>
          <View style={[styles.badge, { backgroundColor: colors.success + '20' }]}>
            <Icon name="checkmark-circle" size={16} color={colors.success} />
            <Text style={[styles.badgeText, { color: colors.success }]}>
              Active Subscription
            </Text>
          </View>
        </GlassCard>

        {/* Topics */}
        <GlassCard style={styles.section}>
          <View style={styles.sectionHeader}>
            <Icon name="list" size={24} color={theme.colors.primary} />
            <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>
              Your Topics
            </Text>
            {!isEditingTopics && (
              <TouchableOpacity
                onPress={() => setIsEditingTopics(true)}
                style={styles.editButton}
              >
                <Text style={[styles.editButtonText, { color: theme.colors.primary }]}>
                  Edit
                </Text>
              </TouchableOpacity>
            )}
          </View>

          {!isEditingTopics ? (
            // Display mode
            <View style={styles.topicsGrid}>
              {topics && topics.length > 0 ? (
                topics.map((topic, index) => (
                  <View
                    key={index}
                    style={[
                      styles.topicChip,
                      {
                        backgroundColor: theme.colors.primary + '20',
                        borderColor: theme.colors.primary,
                      },
                    ]}
                  >
                    <Icon
                      name={getTopicIcon(topic)}
                      size={14}
                      color={theme.colors.primary}
                    />
                    <Text style={[styles.topicChipText, { color: theme.colors.primary }]}>
                      {topic}
                    </Text>
                  </View>
                ))
              ) : (
                <Text style={[styles.emptyText, { color: theme.colors.textSecondary }]}>
                  No topics selected
                </Text>
              )}
            </View>
          ) : (
            // Edit mode
            <>
              <View style={styles.topicsEditGrid}>
                {AVAILABLE_TOPICS.map((topic) => {
                  const isSelected = selectedTopics.includes(topic);
                  return (
                    <TouchableOpacity
                      key={topic}
                      onPress={() => handleToggleTopic(topic)}
                      style={[
                        styles.topicEditChip,
                        {
                          backgroundColor: isSelected
                            ? theme.colors.primary
                            : theme.colors.surface,
                          borderColor: isSelected
                            ? theme.colors.primary
                            : 'transparent',
                        },
                      ]}
                    >
                      <Icon
                        name={getTopicIcon(topic)}
                        size={16}
                        color={isSelected ? 'white' : theme.colors.textSecondary}
                      />
                      <Text
                        style={[
                          styles.topicEditText,
                          {
                            color: isSelected ? 'white' : theme.colors.textPrimary,
                          },
                        ]}
                      >
                        {topic}
                      </Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
              <View style={styles.editActions}>
                <GlassButton
                  onPress={handleCancelEditTopics}
                  variant="secondary"
                  style={styles.actionButton}
                >
                  Cancel
                </GlassButton>
                <GlassButton
                  onPress={handleSaveTopics}
                  variant="primary"
                  style={styles.actionButton}
                  disabled={isLoading}
                >
                  {isLoading ? <ActivityIndicator color="white" /> : 'Save'}
                </GlassButton>
              </View>
            </>
          )}
        </GlassCard>

        {/* Newsletter Preferences */}
        <GlassCard style={styles.section}>
          <View style={styles.sectionHeader}>
            <Icon name="settings" size={24} color={theme.colors.primary} />
            <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>
              Newsletter Style
            </Text>
          </View>
          <Text style={[styles.sectionDescription, { color: theme.colors.textSecondary }]}>
            Choose how you want to receive your daily digest
          </Text>

          <View style={styles.styleOptions}>
            <TouchableOpacity
              onPress={handleToggleNewsletterStyle}
              style={[
                styles.styleOption,
                {
                  backgroundColor:
                    newsletterStyle === 'concise'
                      ? theme.colors.primary
                      : theme.colors.surface,
                },
              ]}
              disabled={isLoading}
            >
              <Icon
                name="flash-outline"
                size={24}
                color={newsletterStyle === 'concise' ? 'white' : theme.colors.textSecondary}
              />
              <Text
                style={[
                  styles.styleOptionText,
                  {
                    color:
                      newsletterStyle === 'concise'
                        ? 'white'
                        : theme.colors.textPrimary,
                  },
                ]}
              >
                Concise
              </Text>
              <Text
                style={[
                  styles.styleOptionDesc,
                  {
                    color:
                      newsletterStyle === 'concise'
                        ? 'rgba(255,255,255,0.8)'
                        : theme.colors.textSecondary,
                  },
                ]}
              >
                Quick headlines
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={handleToggleNewsletterStyle}
              style={[
                styles.styleOption,
                {
                  backgroundColor:
                    newsletterStyle === 'detailed'
                      ? theme.colors.primary
                      : theme.colors.surface,
                },
              ]}
              disabled={isLoading}
            >
              <Icon
                name="document-text-outline"
                size={24}
                color={newsletterStyle === 'detailed' ? 'white' : theme.colors.textSecondary}
              />
              <Text
                style={[
                  styles.styleOptionText,
                  {
                    color:
                      newsletterStyle === 'detailed'
                        ? 'white'
                        : theme.colors.textPrimary,
                  },
                ]}
              >
                Detailed
              </Text>
              <Text
                style={[
                  styles.styleOptionDesc,
                  {
                    color:
                      newsletterStyle === 'detailed'
                        ? 'rgba(255,255,255,0.8)'
                        : theme.colors.textSecondary,
                  },
                ]}
              >
                Full summaries
              </Text>
            </TouchableOpacity>
          </View>
        </GlassCard>

        {/* Danger Zone */}
        <GlassCard style={[styles.section, styles.dangerSection]}>
          <View style={styles.sectionHeader}>
            <Icon name="warning" size={24} color={colors.error} />
            <Text style={[styles.sectionTitle, { color: colors.error }]}>
              Danger Zone
            </Text>
          </View>
          <Text style={[styles.sectionDescription, { color: theme.colors.textSecondary }]}>
            Unsubscribing will remove all your data and stop all email digests
          </Text>
          <GlassButton
            onPress={handleUnsubscribe}
            variant="secondary"
            style={[styles.unsubscribeButton, { borderColor: colors.error }]}
            disabled={isLoading}
          >
            <View style={styles.unsubscribeContent}>
              <Icon name="close-circle-outline" size={20} color={colors.error} />
              <Text style={[styles.unsubscribeText, { color: colors.error }]}>
                Unsubscribe from UP2D8
              </Text>
            </View>
          </GlassButton>
        </GlassCard>
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
    opacity: 0.15,
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
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: spacing[4],
    paddingBottom: spacing[12],
  },
  section: {
    padding: spacing[5],
    marginBottom: spacing[4],
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing[4],
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold as any,
    marginLeft: spacing[2],
    flex: 1,
  },
  sectionDescription: {
    fontSize: typography.fontSize.sm,
    marginBottom: spacing[4],
    lineHeight: typography.fontSize.sm * 1.5,
  },
  editButton: {
    paddingHorizontal: spacing[3],
    paddingVertical: spacing[1],
  },
  editButtonText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold as any,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing[3],
  },
  infoText: {
    fontSize: typography.fontSize.base,
    marginLeft: spacing[2],
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingHorizontal: spacing[3],
    paddingVertical: spacing[2],
    borderRadius: borderRadius.full,
  },
  badgeText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold as any,
    marginLeft: spacing[1],
  },
  topicsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  topicChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing[3],
    paddingVertical: spacing[2],
    borderRadius: borderRadius.full,
    marginRight: spacing[2],
    marginBottom: spacing[2],
    borderWidth: 1,
  },
  topicChipText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium as any,
    marginLeft: spacing[1],
  },
  topicsEditGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: spacing[4],
  },
  topicEditChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing[3],
    paddingVertical: spacing[2],
    borderRadius: borderRadius.lg,
    marginRight: spacing[2],
    marginBottom: spacing[2],
    borderWidth: 1,
  },
  topicEditText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium as any,
    marginLeft: spacing[1],
  },
  editActions: {
    flexDirection: 'row',
    gap: spacing[2],
  },
  actionButton: {
    flex: 1,
  },
  emptyText: {
    fontSize: typography.fontSize.sm,
    fontStyle: 'italic',
  },
  styleOptions: {
    flexDirection: 'row',
    gap: spacing[3],
  },
  styleOption: {
    flex: 1,
    padding: spacing[4],
    borderRadius: borderRadius.lg,
    alignItems: 'center',
  },
  styleOptionText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold as any,
    marginTop: spacing[2],
  },
  styleOptionDesc: {
    fontSize: typography.fontSize.xs,
    marginTop: spacing[1],
  },
  dangerSection: {
    borderWidth: 1,
    borderColor: colors.error + '20',
  },
  unsubscribeButton: {
    marginTop: spacing[2],
  },
  unsubscribeContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing[2],
  },
  unsubscribeText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold as any,
  },
});

export default ProfileScreen;
