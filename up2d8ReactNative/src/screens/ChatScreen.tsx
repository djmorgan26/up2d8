import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { ChatBubble } from '../components/ChatBubble';
import { GlassCard } from '../components/GlassCard';
import Icon from 'react-native-vector-icons/Ionicons';
import LinearGradient from 'react-native-linear-gradient';
import { colors, spacing, typography, borderRadius } from '../theme/tokens';
import { useChatStore } from '../store/chatStore';
import { EXAMPLE_PROMPTS } from '../services/chatService';

const ChatScreen: React.FC = () => {
  const { theme } = useTheme();
  const { messages, isLoading, loadChatHistory, sendMessage, clearChat } = useChatStore();
  const [inputText, setInputText] = useState('');
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    // Load chat history on mount
    loadChatHistory();
  }, []);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    if (messages.length > 0 && flatListRef.current) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  const handleSend = async () => {
    if (!inputText.trim() || isLoading) return;

    const message = inputText.trim();
    setInputText('');

    await sendMessage(message);
  };

  const handleExamplePrompt = (prompt: string) => {
    setInputText(prompt);
  };

  const handleClearChat = () => {
    clearChat();
  };

  const renderEmpty = () => (
    <View style={styles.emptyContainer}>
      <View style={[styles.emptyIcon, { backgroundColor: theme.colors.primary }]}>
        <Icon name="chatbubbles" size={48} color="white" />
      </View>
      <Text style={[styles.emptyTitle, { color: theme.colors.textPrimary }]}>
        Ask me anything about the news
      </Text>
      <Text style={[styles.emptySubtitle, { color: theme.colors.textSecondary }]}>
        I'll search the web and give you answers with sources
      </Text>

      {/* Example Prompts */}
      <View style={styles.examplesContainer}>
        <Text style={[styles.examplesTitle, { color: theme.colors.textSecondary }]}>
          Try asking:
        </Text>
        {EXAMPLE_PROMPTS.slice(0, 3).map((prompt, index) => (
          <TouchableOpacity
            key={index}
            onPress={() => handleExamplePrompt(prompt)}
          >
            <GlassCard style={styles.exampleCard}>
              <Icon
                name="bulb-outline"
                size={16}
                color={theme.colors.primary}
              />
              <Text
                style={[styles.exampleText, { color: theme.colors.textPrimary }]}
              >
                {prompt}
              </Text>
            </GlassCard>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  const renderMessage = ({ item }: { item: any }) => (
    <ChatBubble message={item} />
  );

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <LinearGradient
        colors={[theme.colors.primary, theme.colors.background]}
        style={styles.gradientContainer}
      />

      {/* Header */}
      <View style={[styles.header, { backgroundColor: theme.colors.background }]}>
        <View>
          <Text style={[styles.title, { color: theme.colors.textPrimary }]}>
            AI News Assistant
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            Powered by Google Gemini
          </Text>
        </View>
        {messages.length > 0 && (
          <TouchableOpacity onPress={handleClearChat} style={styles.clearButton}>
            <Icon name="trash-outline" size={20} color={theme.colors.textSecondary} />
          </TouchableOpacity>
        )}
      </View>

      {/* Messages List */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.messagesList}
        ListEmptyComponent={renderEmpty}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      {/* Loading Indicator */}
      {isLoading && (
        <View style={styles.loadingContainer}>
          <GlassCard style={styles.loadingCard}>
            <ActivityIndicator size="small" color={theme.colors.primary} />
            <Text style={[styles.loadingText, { color: theme.colors.textSecondary }]}>
              Thinking...
            </Text>
          </GlassCard>
        </View>
      )}

      {/* Input Area */}
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <View style={[styles.inputContainer, { backgroundColor: theme.colors.background }]}>
          <GlassCard style={styles.inputCard}>
            <TextInput
              style={[styles.input, { color: theme.colors.textPrimary }]}
              placeholder="Ask about the news..."
              placeholderTextColor={theme.colors.textSecondary}
              value={inputText}
              onChangeText={setInputText}
              multiline
              maxLength={500}
              editable={!isLoading}
            />
            <TouchableOpacity
              onPress={handleSend}
              style={[
                styles.sendButton,
                {
                  backgroundColor:
                    inputText.trim() && !isLoading
                      ? theme.colors.primary
                      : theme.colors.surface,
                },
              ]}
              disabled={!inputText.trim() || isLoading}
            >
              <Icon
                name="send"
                size={20}
                color={
                  inputText.trim() && !isLoading
                    ? 'white'
                    : theme.colors.textSecondary
                }
              />
            </TouchableOpacity>
          </GlassCard>
        </View>
      </KeyboardAvoidingView>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
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
  clearButton: {
    padding: spacing[2],
  },
  messagesList: {
    flexGrow: 1,
    paddingTop: spacing[4],
    paddingBottom: spacing[4],
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing[6],
    paddingTop: spacing[12],
  },
  emptyIcon: {
    width: 96,
    height: 96,
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing[6],
    shadowColor: colors.primary[500],
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  emptyTitle: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[2],
    textAlign: 'center',
  },
  emptySubtitle: {
    fontSize: typography.fontSize.base,
    textAlign: 'center',
    marginBottom: spacing[8],
  },
  examplesContainer: {
    width: '100%',
  },
  examplesTitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold as any,
    marginBottom: spacing[3],
  },
  exampleCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing[3],
    marginBottom: spacing[2],
  },
  exampleText: {
    fontSize: typography.fontSize.sm,
    marginLeft: spacing[2],
    flex: 1,
  },
  loadingContainer: {
    paddingHorizontal: spacing[4],
    paddingBottom: spacing[2],
  },
  loadingCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing[3],
    alignSelf: 'flex-start',
  },
  loadingText: {
    fontSize: typography.fontSize.sm,
    marginLeft: spacing[2],
  },
  inputContainer: {
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[3],
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.05)',
  },
  inputCard: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: spacing[2],
  },
  input: {
    flex: 1,
    fontSize: typography.fontSize.base,
    maxHeight: 100,
    paddingHorizontal: spacing[2],
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: spacing[2],
  },
});

export default ChatScreen;
