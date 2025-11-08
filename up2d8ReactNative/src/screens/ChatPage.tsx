import React from 'react';
import { View, Text, StyleSheet, ScrollView, LinearGradient } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import Icon from 'react-native-vector-icons/Ionicons';
import { GlassCard } from '../components/GlassCard';
import { GlassButton } from '../components/GlassButton';
import { colors, spacing, typography, borderRadius } from '../theme/tokens';

const ChatPage: React.FC = () => {
  const { theme } = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Gradient Background */}
      <View style={styles.gradientContainer}>
        <View
          style={[
            styles.gradient,
            {
              backgroundColor: theme.colors.primary,
              opacity: 0.1,
            },
          ]}
        />
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header Section */}
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.colors.textPrimary }]}>
            Messages
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            Stay connected with your conversations
          </Text>
        </View>

        {/* Recent Chats */}
        <GlassCard style={styles.card}>
          <View style={styles.chatItem}>
            <View style={[styles.avatar, { backgroundColor: colors.primary[400] }]}>
              <Icon name="person" size={24} color="white" />
            </View>
            <View style={styles.chatContent}>
              <Text style={[styles.chatName, { color: theme.colors.textPrimary }]}>
                John Doe
              </Text>
              <Text style={[styles.chatMessage, { color: theme.colors.textSecondary }]}>
                Hey! How are you doing?
              </Text>
            </View>
            <Text style={[styles.chatTime, { color: theme.colors.textSecondary }]}>
              2m
            </Text>
          </View>
        </GlassCard>

        <GlassCard style={styles.card}>
          <View style={styles.chatItem}>
            <View style={[styles.avatar, { backgroundColor: colors.accent[400] }]}>
              <Icon name="people" size={24} color="white" />
            </View>
            <View style={styles.chatContent}>
              <Text style={[styles.chatName, { color: theme.colors.textPrimary }]}>
                Team Chat
              </Text>
              <Text style={[styles.chatMessage, { color: theme.colors.textSecondary }]}>
                New updates are available
              </Text>
            </View>
            <Text style={[styles.chatTime, { color: theme.colors.textSecondary }]}>
              15m
            </Text>
          </View>
        </GlassCard>

        <GlassCard style={styles.card}>
          <View style={styles.chatItem}>
            <View style={[styles.avatar, { backgroundColor: colors.primary[600] }]}>
              <Icon name="chatbubbles" size={24} color="white" />
            </View>
            <View style={styles.chatContent}>
              <Text style={[styles.chatName, { color: theme.colors.textPrimary }]}>
                Support
              </Text>
              <Text style={[styles.chatMessage, { color: theme.colors.textSecondary }]}>
                We're here to help!
              </Text>
            </View>
            <Text style={[styles.chatTime, { color: theme.colors.textSecondary }]}>
              1h
            </Text>
          </View>
        </GlassCard>

        {/* Action Button */}
        <GlassButton
          onPress={() => console.log('Start new chat')}
          style={styles.button}
        >
          <View style={styles.buttonContent}>
            <Icon name="add-circle-outline" size={20} color="white" />
            <Text style={styles.buttonText}>Start New Chat</Text>
          </View>
        </GlassButton>
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
    overflow: 'hidden',
  },
  gradient: {
    flex: 1,
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
    marginBottom: spacing[6],
  },
  title: {
    fontSize: typography.fontSize['4xl'],
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[2],
  },
  subtitle: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.regular as any,
  },
  card: {
    marginBottom: spacing[3],
  },
  chatItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing[3],
  },
  chatContent: {
    flex: 1,
  },
  chatName: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold as any,
    marginBottom: spacing[1],
  },
  chatMessage: {
    fontSize: typography.fontSize.sm,
  },
  chatTime: {
    fontSize: typography.fontSize.xs,
  },
  button: {
    marginTop: spacing[4],
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing[2],
  },
  buttonText: {
    color: 'white',
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold as any,
  },
});

export default ChatPage;
