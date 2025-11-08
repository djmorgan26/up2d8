import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Animated,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { GlassCard } from '../components/GlassCard';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/Ionicons';
import ThemeSwitcher from '../components/ThemeSwitcher';
import { haptics } from '../utils/haptics';

const SettingsPage: React.FC = () => {
  const { theme } = useTheme();
  const scaleAnim = React.useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    haptics.light();
    Animated.spring(scaleAnim, {
      toValue: 0.97,
      useNativeDriver: true,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      friction: 5,
      tension: 100,
      useNativeDriver: true,
    }).start();
  };

  const SettingItem = ({
    icon,
    title,
    subtitle,
    onPress,
    showChevron = true,
  }: {
    icon: string;
    title: string;
    subtitle?: string;
    onPress?: () => void;
    showChevron?: boolean;
  }) => (
    <TouchableOpacity
      onPress={onPress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      activeOpacity={0.9}
    >
      <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
        <GlassCard blurIntensity="medium" variant={theme.dark ? 'dark' : 'light'}>
          <View style={styles.settingItem}>
            <View style={styles.settingLeft}>
              <View
                style={[
                  styles.iconContainer,
                  { backgroundColor: theme.colors.primary + '20' },
                ]}
              >
                <Icon name={icon} size={24} color={theme.colors.primary} />
              </View>
              <View style={styles.settingText}>
                <Text style={[styles.settingTitle, { color: theme.colors.textPrimary }]}>
                  {title}
                </Text>
                {subtitle && (
                  <Text
                    style={[styles.settingSubtitle, { color: theme.colors.textSecondary }]}
                  >
                    {subtitle}
                  </Text>
                )}
              </View>
            </View>
            {showChevron && (
              <Icon name="chevron-forward" size={20} color={theme.colors.textSecondary} />
            )}
          </View>
        </GlassCard>
      </Animated.View>
    </TouchableOpacity>
  );

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    header: {
      paddingTop: 60,
      paddingBottom: 20,
      paddingHorizontal: 20,
    },
    headerTitle: {
      fontSize: 34,
      fontWeight: '700',
      color: theme.colors.textPrimary,
      marginBottom: 8,
    },
    headerSubtitle: {
      fontSize: 16,
      color: theme.colors.textSecondary,
      fontWeight: '400',
    },
    scrollContent: {
      padding: 20,
      paddingBottom: 100,
    },
    section: {
      marginBottom: 32,
    },
    sectionTitle: {
      fontSize: 13,
      fontWeight: '600',
      color: theme.colors.textSecondary,
      textTransform: 'uppercase',
      letterSpacing: 0.5,
      marginBottom: 12,
      marginLeft: 4,
    },
    settingItem: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: 16,
    },
    settingLeft: {
      flexDirection: 'row',
      alignItems: 'center',
      flex: 1,
    },
    iconContainer: {
      width: 40,
      height: 40,
      borderRadius: 10,
      alignItems: 'center',
      justifyContent: 'center',
      marginRight: 12,
    },
    settingText: {
      flex: 1,
    },
    settingTitle: {
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 2,
    },
    settingSubtitle: {
      fontSize: 13,
      fontWeight: '400',
    },
    themeCard: {
      marginBottom: 12,
    },
    themeSwitcherContainer: {
      padding: 16,
    },
    infoCard: {
      padding: 20,
      alignItems: 'center',
    },
    appIcon: {
      width: 80,
      height: 80,
      borderRadius: 18,
      marginBottom: 16,
      alignItems: 'center',
      justifyContent: 'center',
    },
    appName: {
      fontSize: 22,
      fontWeight: '700',
      color: theme.colors.textPrimary,
      marginBottom: 4,
    },
    appVersion: {
      fontSize: 14,
      color: theme.colors.textSecondary,
      fontWeight: '400',
    },
  });

  return (
    <View style={styles.container}>
      {/* Header with gradient */}
      <LinearGradient
        colors={[theme.colors.primary, theme.colors.background]}
        start={{ x: 0, y: 0 }}
        end={{ x: 0, y: 1 }}
        style={styles.header}
      >
        <Text style={styles.headerTitle}>Settings</Text>
        <Text style={styles.headerSubtitle}>Customize your experience</Text>
      </LinearGradient>

      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Appearance Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Appearance</Text>
          <GlassCard
            blurIntensity="medium"
            variant={theme.dark ? 'dark' : 'light'}
            style={styles.themeCard}
          >
            <View style={styles.themeSwitcherContainer}>
              <ThemeSwitcher />
            </View>
          </GlassCard>
        </View>

        {/* Account Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Account</Text>
          <SettingItem
            icon="person-outline"
            title="Profile"
            subtitle="Manage your profile information"
            onPress={() => console.log('Profile pressed')}
          />
          <View style={{ height: 12 }} />
          <SettingItem
            icon="notifications-outline"
            title="Notifications"
            subtitle="Manage notification preferences"
            onPress={() => console.log('Notifications pressed')}
          />
          <View style={{ height: 12 }} />
          <SettingItem
            icon="shield-checkmark-outline"
            title="Privacy & Security"
            subtitle="Control your privacy settings"
            onPress={() => console.log('Privacy pressed')}
          />
        </View>

        {/* Content Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Content</Text>
          <SettingItem
            icon="bookmark-outline"
            title="Saved Items"
            subtitle="View your saved content"
            onPress={() => console.log('Saved pressed')}
          />
          <View style={{ height: 12 }} />
          <SettingItem
            icon="time-outline"
            title="Reading History"
            subtitle="See what you've read"
            onPress={() => console.log('History pressed')}
          />
          <View style={{ height: 12 }} />
          <SettingItem
            icon="filter-outline"
            title="Content Preferences"
            subtitle="Customize your feed"
            onPress={() => console.log('Preferences pressed')}
          />
        </View>

        {/* Support Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Support</Text>
          <SettingItem
            icon="help-circle-outline"
            title="Help & FAQ"
            subtitle="Get answers to common questions"
            onPress={() => console.log('Help pressed')}
          />
          <View style={{ height: 12 }} />
          <SettingItem
            icon="chatbubble-ellipses-outline"
            title="Contact Support"
            subtitle="Get in touch with our team"
            onPress={() => console.log('Contact pressed')}
          />
          <View style={{ height: 12 }} />
          <SettingItem
            icon="star-outline"
            title="Rate App"
            subtitle="Enjoying the app? Let us know!"
            onPress={() => console.log('Rate pressed')}
          />
        </View>

        {/* About Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>
          <GlassCard blurIntensity="medium" variant={theme.dark ? 'dark' : 'light'}>
            <View style={styles.infoCard}>
              <LinearGradient
                colors={[theme.colors.primary, theme.colors.accent]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.appIcon}
              >
                <Icon name="newspaper-outline" size={40} color="#FFFFFF" />
              </LinearGradient>
              <Text style={styles.appName}>up2d8</Text>
              <Text style={styles.appVersion}>Version 1.0.0</Text>
            </View>
          </GlassCard>
          <View style={{ height: 12 }} />
          <SettingItem
            icon="document-text-outline"
            title="Terms of Service"
            onPress={() => console.log('Terms pressed')}
          />
          <View style={{ height: 12 }} />
          <SettingItem
            icon="shield-outline"
            title="Privacy Policy"
            onPress={() => console.log('Privacy Policy pressed')}
          />
          <View style={{ height: 12 }} />
          <SettingItem
            icon="code-slash-outline"
            title="Open Source Licenses"
            onPress={() => console.log('Licenses pressed')}
          />
        </View>
      </ScrollView>
    </View>
  );
};

export default SettingsPage;
