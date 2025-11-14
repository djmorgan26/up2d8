/**
 * Login Screen
 * Email/password login with MSAL option
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Pressable,
} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {GlassCard, GlassButton, Input} from '@components/ui';
import {useAuthStore} from '@stores';
import {Mail, Lock, LogIn, AlertCircle} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';
import Toast from 'react-native-toast-message';
import {triggerHaptic} from '@utils/haptics';

interface LoginScreenProps {
  navigation: any;
}

export default function LoginScreen({navigation}: LoginScreenProps) {
  const {theme} = useTheme();
  const {login, isLoading, error} = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      setEmailError('Email is required');
      return false;
    }
    if (!emailRegex.test(email)) {
      setEmailError('Invalid email format');
      return false;
    }
    setEmailError('');
    return true;
  };

  const validatePassword = (password: string): boolean => {
    if (!password) {
      setPasswordError('Password is required');
      return false;
    }
    if (password.length < 6) {
      setPasswordError('Password must be at least 6 characters');
      return false;
    }
    setPasswordError('');
    return true;
  };

  const handleLogin = async () => {
    triggerHaptic('medium');

    const isEmailValid = validateEmail(email);
    const isPasswordValid = validatePassword(password);

    if (!isEmailValid || !isPasswordValid) {
      triggerHaptic('notificationError');
      return;
    }

    try {
      await login(email, password);
      triggerHaptic('notificationSuccess');
      Toast.show({
        type: 'success',
        text1: 'Welcome back!',
        text2: 'Login successful',
      });
    } catch (err: any) {
      triggerHaptic('notificationError');
      Toast.show({
        type: 'error',
        text1: 'Login failed',
        text2: err.message || 'Please check your credentials',
      });
    }
  };

  const handleMSALLogin = () => {
    triggerHaptic('medium');
    // Navigate to MSAL login flow
    navigation.navigate('MSALLogin');
  };

  const handleSignup = () => {
    triggerHaptic('light');
    navigation.navigate('Signup');
  };

  return (
    <KeyboardAvoidingView
      style={[styles.container, {backgroundColor: theme.colors.background}]}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <LinearGradient
            colors={[theme.colors.primary, theme.colors.accent]}
            start={{x: 0, y: 0}}
            end={{x: 1, y: 1}}
            style={[styles.logoContainer, {borderRadius: theme.borderRadius.xl}]}>
            <LogIn size={40} color="#FFFFFF" />
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
            Welcome Back
          </Text>
          <Text
            style={[
              styles.subtitle,
              {
                color: theme.colors.textSecondary,
                fontSize: theme.typography.fontSize.base,
              },
            ]}>
            Sign in to continue to UP2D8
          </Text>
        </View>

        {/* Login Form */}
        <GlassCard style={styles.formCard}>
          {/* Error Banner */}
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

          {/* Email Input */}
          <View style={styles.inputGroup}>
            <Text
              style={[
                styles.label,
                {
                  color: theme.colors.textPrimary,
                  fontSize: theme.typography.fontSize.sm,
                  fontWeight: theme.typography.fontWeight.medium,
                },
              ]}>
              Email
            </Text>
            <Input
              value={email}
              onChangeText={(text) => {
                setEmail(text);
                if (emailError) validateEmail(text);
              }}
              placeholder="your@email.com"
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
              leftIcon={<Mail size={20} color={theme.colors.textSecondary} />}
              error={emailError}
            />
          </View>

          {/* Password Input */}
          <View style={styles.inputGroup}>
            <Text
              style={[
                styles.label,
                {
                  color: theme.colors.textPrimary,
                  fontSize: theme.typography.fontSize.sm,
                  fontWeight: theme.typography.fontWeight.medium,
                },
              ]}>
              Password
            </Text>
            <Input
              value={password}
              onChangeText={(text) => {
                setPassword(text);
                if (passwordError) validatePassword(text);
              }}
              placeholder="Enter your password"
              secureTextEntry
              leftIcon={<Lock size={20} color={theme.colors.textSecondary} />}
              error={passwordError}
            />
          </View>

          {/* Login Button */}
          <GlassButton
            onPress={handleLogin}
            loading={isLoading}
            disabled={isLoading}
            size="lg"
            style={styles.loginButton}>
            Sign In
          </GlassButton>

          {/* Divider */}
          <View style={styles.divider}>
            <View
              style={[styles.dividerLine, {backgroundColor: theme.colors.border}]}
            />
            <Text
              style={[
                styles.dividerText,
                {
                  color: theme.colors.textSecondary,
                  fontSize: theme.typography.fontSize.sm,
                },
              ]}>
              OR
            </Text>
            <View
              style={[styles.dividerLine, {backgroundColor: theme.colors.border}]}
            />
          </View>

          {/* MSAL Button */}
          <GlassButton
            onPress={handleMSALLogin}
            variant="outline"
            disabled={isLoading}
            size="lg">
            Sign in with Microsoft
          </GlassButton>
        </GlassCard>

        {/* Sign Up Link */}
        <View style={styles.footer}>
          <Text
            style={[
              styles.footerText,
              {
                color: theme.colors.textSecondary,
                fontSize: theme.typography.fontSize.sm,
              },
            ]}>
            Don't have an account?{' '}
          </Text>
          <Pressable onPress={handleSignup} disabled={isLoading}>
            <Text
              style={[
                styles.linkText,
                {
                  color: theme.colors.primary,
                  fontSize: theme.typography.fontSize.sm,
                  fontWeight: theme.typography.fontWeight.semibold,
                },
              ]}>
              Sign Up
            </Text>
          </Pressable>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
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
  },
  subtitle: {
    textAlign: 'center',
  },
  formCard: {
    padding: 24,
    marginBottom: 16,
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
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    marginBottom: 8,
  },
  loginButton: {
    marginTop: 8,
    marginBottom: 16,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 16,
    gap: 12,
  },
  dividerLine: {
    flex: 1,
    height: 1,
  },
  dividerText: {},
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  footerText: {},
  linkText: {},
});
