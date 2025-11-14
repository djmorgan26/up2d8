/**
 * MSAL Login Screen
 * Microsoft Entra ID authentication (SSO)
 */

import React, {useState, useEffect} from 'react';
import {View, Text, StyleSheet, ActivityIndicator} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {GlassCard, GlassButton} from '@components/ui';
import {useAuthStore} from '@stores';
import {Shield, AlertCircle, ArrowLeft} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';
import Toast from 'react-native-toast-message';
import {triggerHaptic} from '@utils/haptics';

interface MSALLoginScreenProps {
  navigation: any;
}

export default function MSALLoginScreen({navigation}: MSALLoginScreenProps) {
  const {theme} = useTheme();
  const {setTokens, setUser} = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleMSALLogin = async () => {
    triggerHaptic('medium');
    setIsLoading(true);
    setError(null);

    try {
      const {msalService} = await import('@services/msalService');

      if (!msalService.isReady()) {
        throw new Error('MSAL not configured. Please set up Entra ID credentials in .env');
      }

      // Acquire token interactively
      const result = await msalService.acquireTokenInteractive();

      // Store tokens
      await setTokens(result.accessToken, undefined, 'msal');

      // Set user info
      setUser({
        id: result.account.homeAccountId,
        email: result.account.username,
        name: result.account.name,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });

      triggerHaptic('notificationSuccess');
      Toast.show({
        type: 'success',
        text1: 'Signed in successfully',
        text2: `Welcome ${result.account.name}!`,
      });

      // Navigation will be handled by RootNavigator when isAuthenticated changes
    } catch (err: any) {
      triggerHaptic('notificationError');
      const errorMessage = err.message || 'Failed to sign in with Microsoft';
      setError(errorMessage);
      Toast.show({
        type: 'error',
        text1: 'Sign in failed',
        text2: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoBack = () => {
    triggerHaptic('light');
    navigation.goBack();
  };

  return (
    <View style={[styles.container, {backgroundColor: theme.colors.background}]}>
      {/* Back Button */}
      <View style={styles.backButton}>
        <GlassButton
          variant="ghost"
          size="icon"
          onPress={handleGoBack}
          icon={<ArrowLeft size={24} color={theme.colors.textPrimary} />}
        />
      </View>

      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <LinearGradient
            colors={[theme.colors.primary, theme.colors.accent]}
            start={{x: 0, y: 0}}
            end={{x: 1, y: 1}}
            style={[styles.logoContainer, {borderRadius: theme.borderRadius.xl}]}>
            <Shield size={40} color="#FFFFFF" />
          </LinearGradient>
          <Text
            style={[
              styles.title,
              {
                color: theme.colors.textPrimary,
                fontSize: theme.typography.fontSize['3xl'],
                fontWeight: theme.typography.fontWeight.bold,
              },
            ]}>
            Microsoft Sign In
          </Text>
          <Text
            style={[
              styles.subtitle,
              {
                color: theme.colors.textSecondary,
                fontSize: theme.typography.fontSize.base,
              },
            ]}>
            Use your Microsoft account for secure single sign-on
          </Text>
        </View>

        {/* Info Card */}
        <GlassCard style={styles.infoCard}>
          <View style={styles.infoContent}>
            <Text
              style={[
                styles.infoTitle,
                {
                  color: theme.colors.textPrimary,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.semibold,
                },
              ]}>
              Benefits of Microsoft Sign In
            </Text>
            <View style={styles.benefitsList}>
              <View style={styles.benefitItem}>
                <View
                  style={[
                    styles.benefitDot,
                    {backgroundColor: theme.colors.primary},
                  ]}
                />
                <Text
                  style={[
                    styles.benefitText,
                    {
                      color: theme.colors.textSecondary,
                      fontSize: theme.typography.fontSize.sm,
                    },
                  ]}>
                  Single sign-on across all devices
                </Text>
              </View>
              <View style={styles.benefitItem}>
                <View
                  style={[
                    styles.benefitDot,
                    {backgroundColor: theme.colors.primary},
                  ]}
                />
                <Text
                  style={[
                    styles.benefitText,
                    {
                      color: theme.colors.textSecondary,
                      fontSize: theme.typography.fontSize.sm,
                    },
                  ]}>
                  Enterprise-grade security
                </Text>
              </View>
              <View style={styles.benefitItem}>
                <View
                  style={[
                    styles.benefitDot,
                    {backgroundColor: theme.colors.primary},
                  ]}
                />
                <Text
                  style={[
                    styles.benefitText,
                    {
                      color: theme.colors.textSecondary,
                      fontSize: theme.typography.fontSize.sm,
                    },
                  ]}>
                  No need to remember another password
                </Text>
              </View>
              <View style={styles.benefitItem}>
                <View
                  style={[
                    styles.benefitDot,
                    {backgroundColor: theme.colors.primary},
                  ]}
                />
                <Text
                  style={[
                    styles.benefitText,
                    {
                      color: theme.colors.textSecondary,
                      fontSize: theme.typography.fontSize.sm,
                    },
                  ]}>
                  Works with your organization's account
                </Text>
              </View>
            </View>
          </View>

          {/* Error Message */}
          {error && (
            <View
              style={[
                styles.errorBanner,
                {
                  backgroundColor: theme.colors.destructive + '20',
                  borderRadius: theme.borderRadius.md,
                },
              ]}>
              <AlertCircle size={20} color={theme.colors.destructive} />
              <Text
                style={[
                  styles.errorText,
                  {
                    color: theme.colors.destructive,
                    fontSize: theme.typography.fontSize.sm,
                  },
                ]}>
                {error}
              </Text>
            </View>
          )}

          {/* Sign In Button */}
          <GlassButton
            onPress={handleMSALLogin}
            loading={isLoading}
            disabled={isLoading}
            size="lg"
            style={styles.signInButton}>
            {isLoading ? 'Signing in...' : 'Sign in with Microsoft'}
          </GlassButton>

          {/* Note */}
          <Text
            style={[
              styles.note,
              {
                color: theme.colors.textSecondary,
                fontSize: theme.typography.fontSize.xs,
              },
            ]}>
            You'll be redirected to Microsoft's secure login page
          </Text>
        </GlassCard>

        {/* Implementation Notice */}
        <View
          style={[
            styles.noticeCard,
            {
              backgroundColor: theme.colors.warning + '20',
              borderRadius: theme.borderRadius.md,
            },
          ]}>
          <AlertCircle size={20} color={theme.colors.warning} />
          <Text
            style={[
              styles.noticeText,
              {
                color: theme.colors.textSecondary,
                fontSize: theme.typography.fontSize.sm,
              },
            ]}>
            MSAL integration requires configuration. Please contact your administrator.
          </Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  backButton: {
    paddingTop: 60,
    paddingHorizontal: 16,
  },
  content: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
  },
  logoContainer: {
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
  subtitle: {
    textAlign: 'center',
    paddingHorizontal: 16,
  },
  infoCard: {
    padding: 24,
    marginBottom: 16,
  },
  infoContent: {
    marginBottom: 20,
  },
  infoTitle: {
    marginBottom: 16,
  },
  benefitsList: {
    gap: 12,
  },
  benefitItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  benefitDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  benefitText: {
    flex: 1,
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    gap: 8,
    marginBottom: 16,
  },
  errorText: {
    flex: 1,
  },
  signInButton: {
    marginBottom: 12,
  },
  note: {
    textAlign: 'center',
    lineHeight: 18,
  },
  noticeCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 16,
    gap: 12,
  },
  noticeText: {
    flex: 1,
    lineHeight: 20,
  },
});
