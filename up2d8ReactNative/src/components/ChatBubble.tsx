import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Linking } from 'react-native';
import { GlassCard } from './GlassCard';
import Icon from 'react-native-vector-icons/Ionicons';
import { colors, spacing, typography, borderRadius } from '../theme/tokens';
import { useTheme } from '../context/ThemeContext';
import { ChatMessage } from '../types';

interface ChatBubbleProps {
  message: ChatMessage;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({ message }) => {
  const { theme } = useTheme();
  const isUser = message.role === 'user';

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const openSource = (url: string) => {
    Linking.openURL(url).catch((err) =>
      console.error('Failed to open URL:', err)
    );
  };

  return (
    <View
      style={[
        styles.container,
        isUser ? styles.userContainer : styles.assistantContainer,
      ]}
    >
      {/* Avatar */}
      {!isUser && (
        <View style={[styles.avatar, { backgroundColor: theme.colors.primary }]}>
          <Icon name="sparkles" size={16} color="white" />
        </View>
      )}

      <View style={styles.messageContainer}>
        {/* Message Bubble */}
        <GlassCard
          style={[
            styles.bubble,
            isUser ? styles.userBubble : styles.assistantBubble,
            { backgroundColor: isUser ? theme.colors.primary : theme.colors.surface },
          ]}
          blurIntensity={isUser ? 'light' : 'medium'}
        >
          <Text
            style={[
              styles.messageText,
              { color: isUser ? 'white' : theme.colors.textPrimary },
            ]}
          >
            {message.content}
          </Text>
        </GlassCard>

        {/* Sources (only for assistant messages) */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <View style={styles.sourcesContainer}>
            <Text style={[styles.sourcesTitle, { color: theme.colors.textSecondary }]}>
              Sources:
            </Text>
            {message.sources.map((source, index) => (
              <TouchableOpacity
                key={index}
                onPress={() => openSource(source.web.uri)}
                style={[styles.sourceCard, { backgroundColor: theme.colors.surface }]}
              >
                <Icon name="link-outline" size={16} color={theme.colors.primary} />
                <Text
                  style={[styles.sourceTitle, { color: theme.colors.textPrimary }]}
                  numberOfLines={1}
                >
                  {source.web.title}
                </Text>
                <Icon name="open-outline" size={14} color={theme.colors.textSecondary} />
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* Timestamp */}
        <Text
          style={[
            styles.timestamp,
            { color: theme.colors.textSecondary },
            isUser && styles.timestampRight,
          ]}
        >
          {formatTime(message.timestamp)}
        </Text>
      </View>

      {/* User Avatar */}
      {isUser && (
        <View style={[styles.avatar, { backgroundColor: theme.colors.accent }]}>
          <Icon name="person" size={16} color="white" />
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    marginBottom: spacing[4],
    paddingHorizontal: spacing[4],
  },
  userContainer: {
    justifyContent: 'flex-end',
  },
  assistantContainer: {
    justifyContent: 'flex-start',
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing[1],
  },
  messageContainer: {
    maxWidth: '75%',
    marginHorizontal: spacing[2],
  },
  bubble: {
    padding: spacing[3],
    marginBottom: spacing[1],
  },
  userBubble: {
    borderTopRightRadius: 4,
  },
  assistantBubble: {
    borderTopLeftRadius: 4,
  },
  messageText: {
    fontSize: typography.fontSize.base,
    lineHeight: typography.fontSize.base * 1.5,
  },
  sourcesContainer: {
    marginTop: spacing[2],
  },
  sourcesTitle: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.semibold as any,
    marginBottom: spacing[2],
  },
  sourceCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing[2],
    borderRadius: borderRadius.md,
    marginBottom: spacing[1],
  },
  sourceTitle: {
    flex: 1,
    fontSize: typography.fontSize.xs,
    marginLeft: spacing[2],
    marginRight: spacing[1],
  },
  timestamp: {
    fontSize: typography.fontSize.xs,
    marginTop: spacing[1],
  },
  timestampRight: {
    textAlign: 'right',
  },
});
