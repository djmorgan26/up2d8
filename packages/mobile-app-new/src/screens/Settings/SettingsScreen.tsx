/**
 * Settings Screen
 * App settings and preferences
 */

import React from 'react';
import {View, Text, ScrollView, StyleSheet} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {GlassCard, GlassButton} from '@components/ui';
import {Settings, Sun, Moon} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';

export default function SettingsScreen() {
  const {theme, toggleTheme, isDark} = useTheme();

  return (
    <View style={[styles.container, {backgroundColor: theme.colors.background}]}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <LinearGradient
            colors={[theme.colors.primary, theme.colors.accent]}
            start={{x: 0, y: 0}}
            end={{x: 1, y: 1}}
            style={[styles.headerIcon, {borderRadius: theme.borderRadius.xl}]}>
            <Settings size={24} color="#FFFFFF" />
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
              Settings
            </Text>
            <Text
              style={[
                styles.headerSubtitle,
                {
                  color: theme.colors.textSecondary,
                  fontSize: theme.typography.fontSize.sm,
                },
              ]}>
              Customize your experience
            </Text>
          </View>
        </View>

        {/* Appearance */}
        <GlassCard style={styles.section}>
          <Text
            style={[
              styles.sectionTitle,
              {
                color: theme.colors.textPrimary,
                fontSize: theme.typography.fontSize.lg,
                fontWeight: theme.typography.fontWeight.semibold,
              },
            ]}>
            Appearance
          </Text>
          <GlassButton
            onPress={toggleTheme}
            icon={
              isDark ? (
                <Sun size={20} color="#FFFFFF" />
              ) : (
                <Moon size={20} color="#FFFFFF" />
              )
            }
            iconPosition="left">
            {isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          </GlassButton>
        </GlassCard>

        {/* App Info */}
        <GlassCard style={styles.section}>
          <Text
            style={[
              styles.sectionTitle,
              {
                color: theme.colors.textPrimary,
                fontSize: theme.typography.fontSize.lg,
                fontWeight: theme.typography.fontWeight.semibold,
              },
            ]}>
            About
          </Text>
          <View style={styles.infoRow}>
            <Text
              style={[
                styles.infoLabel,
                {
                  color: theme.colors.textSecondary,
                  fontSize: theme.typography.fontSize.base,
                },
              ]}>
              Version
            </Text>
            <Text
              style={[
                styles.infoValue,
                {
                  color: theme.colors.textPrimary,
                  fontSize: theme.typography.fontSize.base,
                  fontWeight: theme.typography.fontWeight.semibold,
                },
              ]}>
              1.0.0 (Phase 3)
            </Text>
          </View>
          <View style={styles.infoRow}>
            <Text
              style={[
                styles.infoLabel,
                {
                  color: theme.colors.textSecondary,
                  fontSize: theme.typography.fontSize.base,
                },
              ]}>
              Status
            </Text>
            <Text
              style={[
                styles.infoValue,
                {
                  color: theme.colors.success,
                  fontSize: theme.typography.fontSize.base,
                  fontWeight: theme.typography.fontWeight.semibold,
                },
              ]}>
              Development
            </Text>
          </View>
        </GlassCard>
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
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 24,
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
  section: {
    marginBottom: 16,
  },
  sectionTitle: {
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  infoLabel: {},
  infoValue: {},
});
