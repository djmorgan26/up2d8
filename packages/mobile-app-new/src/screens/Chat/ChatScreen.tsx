/**
 * Chat Screen
 * AI chat interface - simplified for now
 */

import React from 'react';
import {View, Text, StyleSheet} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {GlassCard} from '@components/ui';
import {MessageSquare} from 'lucide-react-native';

export default function ChatScreen() {
  const {theme} = useTheme();

  return (
    <View style={[styles.container, {backgroundColor: theme.colors.background}]}>
      <View style={styles.content}>
        <GlassCard style={styles.card}>
          <View style={styles.emptyContent}>
            <View
              style={[
                styles.icon,
                {
                  backgroundColor: theme.colors.muted,
                  borderRadius: theme.borderRadius.full,
                },
              ]}>
              <MessageSquare size={40} color={theme.colors.textSecondary} />
            </View>
            <Text
              style={[
                styles.title,
                {
                  color: theme.colors.textPrimary,
                  fontSize: theme.typography.fontSize.xl,
                  fontWeight: theme.typography.fontWeight.semibold,
                },
              ]}>
              Chat Coming Soon
            </Text>
            <Text
              style={[
                styles.text,
                {
                  color: theme.colors.textSecondary,
                  fontSize: theme.typography.fontSize.base,
                },
              ]}>
              AI chat will be implemented in Phase 5
            </Text>
          </View>
        </GlassCard>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    padding: 16,
    justifyContent: 'center',
  },
  card: {
    padding: 32,
  },
  emptyContent: {
    alignItems: 'center',
  },
  icon: {
    width: 80,
    height: 80,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    marginBottom: 8,
    textAlign: 'center',
  },
  text: {
    textAlign: 'center',
    lineHeight: 24,
  },
});
