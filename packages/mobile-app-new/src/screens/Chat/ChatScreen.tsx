/**
 * Chat Screen
 * AI chat interface with conversation history
 */

import React, {useState, useRef} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Alert,
  Linking,
  Pressable,
} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {GlassCard, GlassButton, Input} from '@components/ui';
import {useChatStore, ChatMessage} from '@stores';
import {sendChatMessage} from '@up2d8/shared-api';
import {
  MessageSquare,
  Send,
  Trash2,
  Bot,
  User,
  ExternalLink,
} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';
import {getRelativeTime} from '@up2d8/shared-utils';

export default function ChatScreen() {
  const {theme} = useTheme();
  const {messages, addMessage, setLoading, isLoading, clearMessages} =
    useChatStore();
  const [input, setInput] = useState('');
  const flatListRef = useRef<FlatList>(null);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message
    addMessage({
      role: 'user',
      content: userMessage,
    });

    // Scroll to bottom
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({animated: true});
    }, 100);

    setLoading(true);

    try {
      const response = await sendChatMessage(userMessage);
      const assistantMessage = response.data.message || response.data.response;

      // Add assistant message
      addMessage({
        role: 'assistant',
        content: assistantMessage,
        sources: response.data.sources,
      });

      // Scroll to bottom
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({animated: true});
      }, 100);
    } catch (error: any) {
      Alert.alert(
        'Error',
        error.response?.data?.error || 'Failed to send message. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    Alert.alert(
      'Clear Chat',
      'Are you sure you want to clear all messages?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Clear',
          style: 'destructive',
          onPress: clearMessages,
        },
      ]
    );
  };

  const handleOpenSource = async (url: string) => {
    try {
      const canOpen = await Linking.canOpenURL(url);
      if (canOpen) {
        await Linking.openURL(url);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to open link');
    }
  };

  const renderMessage = ({item}: {item: ChatMessage}) => {
    const isUser = item.role === 'user';

    return (
      <View
        style={[
          styles.messageContainer,
          isUser ? styles.userMessageContainer : styles.assistantMessageContainer,
        ]}>
        {/* Avatar */}
        <View
          style={[
            styles.avatar,
            {
              backgroundColor: isUser
                ? theme.colors.primary + '20'
                : theme.colors.accent + '20',
              borderRadius: theme.borderRadius.full,
            },
          ]}>
          {isUser ? (
            <User size={16} color={theme.colors.primary} />
          ) : (
            <Bot size={16} color={theme.colors.accent} />
          )}
        </View>

        {/* Message Bubble */}
        <View style={styles.messageBubble}>
          <GlassCard
            style={[
              styles.messageCard,
              {
                backgroundColor: isUser
                  ? theme.colors.primary + '15'
                  : theme.colors.card,
              },
            ]}>
            <Text
              style={[
                styles.messageText,
                {
                  color: theme.colors.textPrimary,
                  fontSize: theme.typography.fontSize.base,
                  lineHeight: theme.typography.fontSize.base * 1.5,
                },
              ]}>
              {item.content}
            </Text>

            {/* Sources */}
            {item.sources && item.sources.length > 0 && (
              <View style={styles.sources}>
                <Text
                  style={[
                    styles.sourcesLabel,
                    {
                      color: theme.colors.textSecondary,
                      fontSize: theme.typography.fontSize.xs,
                      fontWeight: theme.typography.fontWeight.semibold,
                    },
                  ]}>
                  SOURCES
                </Text>
                {item.sources.map((source, index) => (
                  <Pressable
                    key={index}
                    style={[
                      styles.sourceItem,
                      {
                        backgroundColor: theme.colors.muted,
                        borderRadius: theme.borderRadius.md,
                      },
                    ]}
                    onPress={() => handleOpenSource(source.url)}>
                    <ExternalLink size={12} color={theme.colors.primary} />
                    <Text
                      style={[
                        styles.sourceText,
                        {
                          color: theme.colors.primary,
                          fontSize: theme.typography.fontSize.sm,
                        },
                      ]}
                      numberOfLines={1}>
                      {source.title}
                    </Text>
                  </Pressable>
                ))}
              </View>
            )}

            <Text
              style={[
                styles.timestamp,
                {
                  color: theme.colors.textTertiary,
                  fontSize: theme.typography.fontSize.xs,
                },
              ]}>
              {getRelativeTime(item.timestamp)}
            </Text>
          </GlassCard>
        </View>
      </View>
    );
  };

  const renderEmpty = () => (
    <View style={styles.emptyContainer}>
      <View
        style={[
          styles.emptyIcon,
          {
            backgroundColor: theme.colors.muted,
            borderRadius: theme.borderRadius.full,
          },
        ]}>
        <MessageSquare size={40} color={theme.colors.textSecondary} />
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
        Ask UP2D8 AI
      </Text>
      <Text
        style={[
          styles.emptyText,
          {
            color: theme.colors.textSecondary,
            fontSize: theme.typography.fontSize.base,
          },
        ]}>
        Get insights and summaries from your personalized news feed. Ask me anything!
      </Text>
    </View>
  );

  return (
    <KeyboardAvoidingView
      style={[styles.container, {backgroundColor: theme.colors.background}]}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={100}>
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
        <View style={styles.headerLeft}>
          <LinearGradient
            colors={[theme.colors.primary, theme.colors.accent]}
            start={{x: 0, y: 0}}
            end={{x: 1, y: 1}}
            style={[
              styles.headerIcon,
              {borderRadius: theme.borderRadius.xl},
            ]}>
            <MessageSquare size={24} color="#FFFFFF" />
          </LinearGradient>
          <View>
            <Text
              style={[
                styles.headerTitle,
                {
                  color: theme.colors.textPrimary,
                  fontSize: theme.typography.fontSize['2xl'],
                  fontWeight: theme.typography.fontWeight.bold,
                },
              ]}>
              Chat
            </Text>
            <Text
              style={[
                styles.headerSubtitle,
                {
                  color: theme.colors.textSecondary,
                  fontSize: theme.typography.fontSize.sm,
                },
              ]}>
              {messages.length} {messages.length === 1 ? 'message' : 'messages'}
            </Text>
          </View>
        </View>

        {messages.length > 0 && (
          <GlassButton
            variant="ghost"
            size="icon"
            onPress={handleClearChat}
            icon={<Trash2 size={20} color={theme.colors.error} />}
          />
        )}
      </View>

      {/* Messages */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        contentContainerStyle={[
          styles.messagesList,
          messages.length === 0 && styles.messagesListEmpty,
        ]}
        ListEmptyComponent={renderEmpty}
        showsVerticalScrollIndicator={false}
        onContentSizeChange={() =>
          flatListRef.current?.scrollToEnd({animated: true})
        }
      />

      {/* Input */}
      <View
        style={[
          styles.inputContainer,
          {
            backgroundColor: theme.colors.card,
            borderTopWidth: 1,
            borderTopColor: theme.colors.border,
          },
        ]}>
        <Input
          value={input}
          onChangeText={setInput}
          placeholder="Ask about your news..."
          multiline
          maxLength={500}
          onSubmitEditing={handleSend}
          returnKeyType="send"
          style={styles.input}
        />
        <GlassButton
          onPress={handleSend}
          disabled={!input.trim() || isLoading}
          loading={isLoading}
          size="icon"
          icon={<Send size={20} color="#FFFFFF" />}
        />
      </View>

      {input.length > 0 && (
        <Text
          style={[
            styles.charCount,
            {
              color: theme.colors.textTertiary,
              fontSize: theme.typography.fontSize.xs,
            },
          ]}>
          {input.length}/500
        </Text>
      )}
    </KeyboardAvoidingView>
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
    paddingHorizontal: 16,
    paddingVertical: 12,
    paddingTop: 50, // Account for status bar
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
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
  messagesList: {
    padding: 16,
    paddingBottom: 8,
  },
  messagesListEmpty: {
    flex: 1,
    justifyContent: 'center',
  },
  emptyContainer: {
    alignItems: 'center',
    paddingHorizontal: 32,
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
  messageContainer: {
    flexDirection: 'row',
    marginBottom: 16,
    gap: 8,
  },
  userMessageContainer: {
    justifyContent: 'flex-end',
  },
  assistantMessageContainer: {
    justifyContent: 'flex-start',
  },
  avatar: {
    width: 32,
    height: 32,
    justifyContent: 'center',
    alignItems: 'center',
  },
  messageBubble: {
    flex: 1,
    maxWidth: '80%',
  },
  messageCard: {
    padding: 12,
  },
  messageText: {
    marginBottom: 4,
  },
  sources: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.1)',
  },
  sourcesLabel: {
    marginBottom: 6,
    letterSpacing: 1,
  },
  sourceItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    padding: 8,
    marginBottom: 4,
  },
  sourceText: {
    flex: 1,
  },
  timestamp: {
    marginTop: 4,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 8,
    padding: 16,
    paddingBottom: 24,
  },
  input: {
    flex: 1,
  },
  charCount: {
    position: 'absolute',
    bottom: 8,
    right: 72,
  },
});
