/**
 * Settings Screen
 * App settings and user preferences
 */

import React from 'react';
import {View, Text, ScrollView, StyleSheet, Switch, Alert} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {GlassCard, GlassButton} from '@components/ui';
import {usePreferencesStore} from '@stores';
import {haptics} from '@utils';
import {
  Settings,
  Sun,
  Moon,
  Bell,
  Eye,
  Type,
  Layout,
  Trash2,
} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';

export default function SettingsScreen() {
  const {theme, toggleTheme, isDark} = useTheme();
  const {preferences, setPreference, resetPreferences} = usePreferencesStore();

  const handleThemeToggle = () => {
    haptics.selection();
    toggleTheme();
  };

  const handleToggleSwitch = (key: keyof typeof preferences) => {
    haptics.selection();
    setPreference(key, !preferences[key]);
  };

  const handleResetPreferences = () => {
    Alert.alert(
      'Reset Preferences',
      'Are you sure you want to reset all preferences to default values?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Reset',
          style: 'destructive',
          onPress: () => {
            haptics.warning();
            resetPreferences();
            Alert.alert('Success', 'Preferences reset to default values');
          },
        },
      ]
    );
  };

  const fontSizeOptions: Array<'small' | 'medium' | 'large'> = [
    'small',
    'medium',
    'large',
  ];

  const handleFontSizeChange = (size: 'small' | 'medium' | 'large') => {
    haptics.selection();
    setPreference('fontSize', size);
  };

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
          <View style={styles.sectionHeader}>
            <Sun size={18} color={theme.colors.primary} />
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
          </View>

          <View style={styles.settingRow}>
            <Text
              style={[
                styles.settingLabel,
                {
                  color: theme.colors.textPrimary,
                  fontSize: theme.typography.fontSize.base,
                },
              ]}>
              Theme
            </Text>
            <GlassButton
              size="sm"
              onPress={handleThemeToggle}
              icon={
                isDark ? (
                  <Sun size={16} color="#FFFFFF" />
                ) : (
                  <Moon size={16} color="#FFFFFF" />
                )
              }
              iconPosition="left">
              {isDark ? 'Light' : 'Dark'}
            </GlassButton>
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text
                style={[
                  styles.settingLabel,
                  {
                    color: theme.colors.textPrimary,
                    fontSize: theme.typography.fontSize.base,
                  },
                ]}>
                Font Size
              </Text>
              <Text
                style={[
                  styles.settingDescription,
                  {
                    color: theme.colors.textSecondary,
                    fontSize: theme.typography.fontSize.sm,
                  },
                ]}>
                Adjust text size for better readability
              </Text>
            </View>
          </View>
          <View style={styles.fontSizeRow}>
            {fontSizeOptions.map(size => (
              <GlassButton
                key={size}
                size="sm"
                variant={preferences.fontSize === size ? 'default' : 'outline'}
                onPress={() => handleFontSizeChange(size)}
                style={{flex: 1}}>
                {size.charAt(0).toUpperCase() + size.slice(1)}
              </GlassButton>
            ))}
          </View>
        </GlassCard>

        {/* Display Preferences */}
        <GlassCard style={styles.section}>
          <View style={styles.sectionHeader}>
            <Eye size={18} color={theme.colors.primary} />
            <Text
              style={[
                styles.sectionTitle,
                {
                  color: theme.colors.textPrimary,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.semibold,
                },
              ]}>
              Display
            </Text>
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text
                style={[
                  styles.settingLabel,
                  {
                    color: theme.colors.textPrimary,
                    fontSize: theme.typography.fontSize.base,
                  },
                ]}>
                Show Images
              </Text>
              <Text
                style={[
                  styles.settingDescription,
                  {
                    color: theme.colors.textSecondary,
                    fontSize: theme.typography.fontSize.sm,
                  },
                ]}>
                Display article images in feed
              </Text>
            </View>
            <Switch
              value={preferences.showImages}
              onValueChange={() => handleToggleSwitch('showImages')}
              trackColor={{
                false: theme.colors.muted,
                true: theme.colors.primary,
              }}
              thumbColor="#FFFFFF"
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text
                style={[
                  styles.settingLabel,
                  {
                    color: theme.colors.textPrimary,
                    fontSize: theme.typography.fontSize.base,
                  },
                ]}>
                Compact View
              </Text>
              <Text
                style={[
                  styles.settingDescription,
                  {
                    color: theme.colors.textSecondary,
                    fontSize: theme.typography.fontSize.sm,
                  },
                ]}>
                Show more articles in less space
              </Text>
            </View>
            <Switch
              value={preferences.compactView}
              onValueChange={() => handleToggleSwitch('compactView')}
              trackColor={{
                false: theme.colors.muted,
                true: theme.colors.primary,
              }}
              thumbColor="#FFFFFF"
            />
          </View>
        </GlassCard>

        {/* Notification Preferences */}
        <GlassCard style={styles.section}>
          <View style={styles.sectionHeader}>
            <Bell size={18} color={theme.colors.primary} />
            <Text
              style={[
                styles.sectionTitle,
                {
                  color: theme.colors.textPrimary,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.semibold,
                },
              ]}>
              Notifications
            </Text>
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text
                style={[
                  styles.settingLabel,
                  {
                    color: theme.colors.textPrimary,
                    fontSize: theme.typography.fontSize.base,
                  },
                ]}>
                Push Notifications
              </Text>
              <Text
                style={[
                  styles.settingDescription,
                  {
                    color: theme.colors.textSecondary,
                    fontSize: theme.typography.fontSize.sm,
                  },
                ]}>
                Get notified about new articles
              </Text>
            </View>
            <Switch
              value={preferences.pushNotificationsEnabled}
              onValueChange={() =>
                handleToggleSwitch('pushNotificationsEnabled')
              }
              trackColor={{
                false: theme.colors.muted,
                true: theme.colors.primary,
              }}
              thumbColor="#FFFFFF"
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text
                style={[
                  styles.settingLabel,
                  {
                    color: theme.colors.textPrimary,
                    fontSize: theme.typography.fontSize.base,
                  },
                ]}>
                Email Notifications
              </Text>
              <Text
                style={[
                  styles.settingDescription,
                  {
                    color: theme.colors.textSecondary,
                    fontSize: theme.typography.fontSize.sm,
                  },
                ]}>
                Receive daily digest via email
              </Text>
            </View>
            <Switch
              value={preferences.emailNotificationsEnabled}
              onValueChange={() =>
                handleToggleSwitch('emailNotificationsEnabled')
              }
              trackColor={{
                false: theme.colors.muted,
                true: theme.colors.primary,
              }}
              thumbColor="#FFFFFF"
            />
          </View>
        </GlassCard>

        {/* Reset */}
        <GlassCard style={styles.section}>
          <Text
            style={[
              styles.sectionTitle,
              {
                color: theme.colors.textPrimary,
                fontSize: theme.typography.fontSize.lg,
                fontWeight: theme.typography.fontWeight.semibold,
                marginBottom: 8,
              },
            ]}>
            Reset
          </Text>
          <Text
            style={[
              styles.settingDescription,
              {
                color: theme.colors.textSecondary,
                fontSize: theme.typography.fontSize.sm,
                marginBottom: 12,
              },
            ]}>
            Reset all preferences to their default values
          </Text>
          <GlassButton
            variant="destructive"
            onPress={handleResetPreferences}
            icon={<Trash2 size={20} color="#FFFFFF" />}
            iconPosition="left">
            Reset All Preferences
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
              1.0.0 (Phase 6)
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
              Beta
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
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
  },
  sectionTitle: {},
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
  },
  settingInfo: {
    flex: 1,
    marginRight: 12,
  },
  settingLabel: {
    marginBottom: 2,
  },
  settingDescription: {
    lineHeight: 18,
  },
  fontSizeRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
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
