import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import Icon from 'react-native-vector-icons/Ionicons';
import { GlassCard } from '../components/GlassCard';
import { GlassButton } from '../components/GlassButton';
import { sendChatMessage, EXAMPLE_PROMPTS } from '../services/chatService';
import { getErrorMessage } from '../services/api';
import { triggerHaptic } from '../utils/haptics';
import {
  colors,
  spacing,
  typography,
  borderRadius,
} from '../theme/tokens';
import LinearGradient from 'react-native-linear-gradient';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  sources?: Array<{ web: { uri: string; title: string } }>;
}

const ChatPage: React.FC = () => {
  const { theme } = useTheme();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (scrollViewRef.current && messages.length > 0) {
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    triggerHaptic('light');

    try {
      const response = await sendChatMessage(userMessage.text);

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.text,
        isUser: false,
        timestamp: new Date(),
        sources: response.sources,
      };

      setMessages(prev => [...prev, aiMessage]);
      triggerHaptic('success');
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      Alert.alert('Error', errorMessage);
      triggerHaptic('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExamplePrompt = (prompt: string) => {
    setInputText(prompt);
    triggerHaptic('light');
  };

  const renderMessage = (message: Message) => {
    const isUser = message.isUser;
    const backgroundColor = isUser
      ? theme.colors.primary
      : theme.colors.surface;

    return (
      <View
        key={message.id}
        style={[
          styles.messageContainer,
          isUser ? styles.userMessage : styles.aiMessage,
        ]}
      >
        <View
          style={[
            styles.messageBubble,
            { backgroundColor },
            isUser && styles.userBubble,
          ]}
        >
          <Text
            style={[
              styles.messageText,
              { color: isUser ? 'white' : theme.colors.textPrimary },
            ]}
          >
            {message.text}
          </Text>

          {message.sources && message.sources.length > 0 && (
            <View style={styles.sourcesContainer}>
              <Text
                style={[styles.sourcesLabel, { color: theme.colors.textSecondary }]}
              >
                Sources:
              </Text>
              {message.sources.map((source, index) => (
                <TouchableOpacity key={index} style={styles.sourceItem}>
                  <Icon name="link-outline" size={14} color={theme.colors.primary} />
                  <Text
                    style={[styles.sourceText, { color: theme.colors.primary }]}
                    numberOfLines={1}
                  >
                    {source.web.title}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>

        <Text style={[styles.timestamp, { color: theme.colors.textTertiary }]}>
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </Text>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      <LinearGradient
        colors={[theme.colors.primary, theme.colors.background]}
        style={styles.gradientContainer}
      />

      {/* Header */}
      <View style={styles.header}>
        <Text style={[styles.title, { color: theme.colors.textPrimary }]}>
          Chat with AI
        </Text>
        <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
          Powered by Google Gemini
        </Text>
      </View>

      {/* Messages or Example Prompts */}
      <ScrollView
        ref={scrollViewRef}
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {messages.length === 0 ? (
          <View style={styles.examplePromptsContainer}>
            <Text
              style={[styles.examplePromptsTitle, { color: theme.colors.textPrimary }]}
            >
              Try asking me about:
            </Text>
            {EXAMPLE_PROMPTS.map((prompt, index) => (
              <TouchableOpacity
                key={index}
                onPress={() => handleExamplePrompt(prompt)}
              >
                <GlassCard style={styles.examplePromptCard}>
                  <Icon
                    name="chatbubble-outline"
                    size={20}
                    color={theme.colors.primary}
                  />
                  <Text
                    style={[
                      styles.examplePromptText,
                      { color: theme.colors.textPrimary },
                    ]}
                  >
                    {prompt}
                  </Text>
                </GlassCard>
              </TouchableOpacity>
            ))}
          </View>
        ) : (
          <View style={styles.messagesContainer}>
            {messages.map(renderMessage)}
            {isLoading && (
              <View style={styles.loadingContainer}>
                <GlassCard style={styles.loadingBubble}>
                  <ActivityIndicator color={theme.colors.primary} />
                  <Text
                    style={[
                      styles.loadingText,
                      { color: theme.colors.textSecondary },
                    ]}
                  >
                    Thinking...
                  </Text>
                </GlassCard>
              </View>
            )}
          </View>
        )}
      </ScrollView>

      {/* Input Area */}
      <View style={[styles.inputContainer, { backgroundColor: theme.colors.surface }]}>
        <TextInput
          style={[
            styles.input,
            {
              color: theme.colors.textPrimary,
              backgroundColor: theme.colors.background,
            },
          ]}
          placeholder="Ask me anything..."
          placeholderTextColor={theme.colors.textTertiary}
          value={inputText}
          onChangeText={setInputText}
          onSubmitEditing={handleSendMessage}
          returnKeyType="send"
          multiline
          maxLength={500}
          editable={!isLoading}
        />

        <TouchableOpacity
          style={[
            styles.sendButton,
            { backgroundColor: inputText.trim() ? theme.colors.primary : theme.colors.surface },
          ]}
          onPress={handleSendMessage}
          disabled={!inputText.trim() || isLoading}
        >
          <Icon
            name="send"
            size={20}
            color={inputText.trim() ? 'white' : theme.colors.textTertiary}
          />
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
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
    height: 200,
    opacity: 0.1,
    borderBottomLeftRadius: borderRadius['3xl'],
    borderBottomRightRadius: borderRadius['3xl'],
  },
  header: {
    marginTop: spacing[8],
    marginBottom: spacing[4],
    paddingHorizontal: spacing[4],
  },
  title: {
    fontSize: typography.fontSize['4xl'],
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[1],
  },
  subtitle: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.regular as any,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: spacing[4],
    paddingBottom: spacing[4],
  },
  examplePromptsContainer: {
    marginTop: spacing[4],
  },
  examplePromptsTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semibold as any,
    marginBottom: spacing[3],
  },
  examplePromptCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing[4],
    marginBottom: spacing[2],
  },
  examplePromptText: {
    fontSize: typography.fontSize.sm,
    marginLeft: spacing[3],
    flex: 1,
  },
  messagesContainer: {
    paddingTop: spacing[2],
  },
  messageContainer: {
    marginBottom: spacing[4],
  },
  userMessage: {
    alignItems: 'flex-end',
  },
  aiMessage: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: spacing[3],
    borderRadius: borderRadius.xl,
  },
  userBubble: {
    borderBottomRightRadius: spacing[1],
  },
  messageText: {
    fontSize: typography.fontSize.base,
    lineHeight: typography.lineHeight.relaxed * typography.fontSize.base,
  },
  sourcesContainer: {
    marginTop: spacing[2],
    paddingTop: spacing[2],
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.1)',
  },
  sourcesLabel: {
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.semibold as any,
    marginBottom: spacing[1],
  },
  sourceItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing[1],
  },
  sourceText: {
    fontSize: typography.fontSize.xs,
    marginLeft: spacing[1],
    flex: 1,
  },
  timestamp: {
    fontSize: typography.fontSize.xs,
    marginTop: spacing[1],
  },
  loadingContainer: {
    alignItems: 'flex-start',
    marginBottom: spacing[4],
  },
  loadingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing[3],
  },
  loadingText: {
    fontSize: typography.fontSize.sm,
    marginLeft: spacing[2],
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: spacing[3],
    borderTopWidth: 1,
    borderTopColor: 'rgba(0, 0, 0, 0.1)',
  },
  input: {
    flex: 1,
    minHeight: 40,
    maxHeight: 100,
    borderRadius: borderRadius.xl,
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[2],
    fontSize: typography.fontSize.base,
    marginRight: spacing[2],
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

export default ChatPage;
