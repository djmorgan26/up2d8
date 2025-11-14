/**
 * Signup Screen
 * User registration with email/password
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
import {Mail, Lock, User, AlertCircle} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';
import Toast from 'react-native-toast-message';
import {triggerHaptic} from '@utils/haptics';

interface SignupScreenProps {
  navigation: any;
}

export default function SignupScreen({navigation}: SignupScreenProps) {
  const {theme} = useTheme();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const [nameError, setNameError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');

  const validateName = (name: string): boolean => {
    if (!name.trim()) {
      setNameError('Name is required');
      return false;
    }
    if (name.trim().length < 2) {
      setNameError('Name must be at least 2 characters');
      return false;
    }
    setNameError('');
    return true;
  };

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
    if (password.length < 8) {
      setPasswordError('Password must be at least 8 characters');
      return false;
    }
    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      setPasswordError('Password must include uppercase, lowercase, and number');
      return false;
    }
    setPasswordError('');
    return true;
  };

  const validateConfirmPassword = (confirmPassword: string): boolean => {
    if (!confirmPassword) {
      setConfirmPasswordError('Please confirm your password');
      return false;
    }
    if (confirmPassword !== password) {
      setConfirmPasswordError('Passwords do not match');
      return false;
    }
    setConfirmPasswordError('');
    return true;
  };

  const handleSignup = async () => {
    triggerHaptic('medium');

    const isNameValid = validateName(name);
    const isEmailValid = validateEmail(email);
    const isPasswordValid = validatePassword(password);
    const isConfirmPasswordValid = validateConfirmPassword(confirmPassword);

    if (!isNameValid || !isEmailValid || !isPasswordValid || !isConfirmPasswordValid) {
      triggerHaptic('notificationError');
      return;
    }

    setIsLoading(true);

    try {
      // TODO: Implement signup API call
      // const response = await apiClient.post('/auth/signup', {name, email, password});
      // await useAuthStore.getState().setTokens(response.data.access_token, response.data.refresh_token);
      // useAuthStore.getState().setUser(response.data.user);

      triggerHaptic('notificationSuccess');
      Toast.show({
        type: 'success',
        text1: 'Account created!',
        text2: 'Welcome to UP2D8',
      });

      // Navigate to main app or show MSAL option
      navigation.replace('MSALLogin');
    } catch (err: any) {
      triggerHaptic('notificationError');
      Toast.show({
        type: 'error',
        text1: 'Signup failed',
        text2: err.message || 'Please try again',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = () => {
    triggerHaptic('light');
    navigation.goBack();
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
            <User size={40} color="#FFFFFF" />
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
            Create Account
          </Text>
          <Text
            style={[
              styles.subtitle,
              {
                color: theme.colors.textSecondary,
                fontSize: theme.typography.fontSize.base,
              },
            ]}>
            Sign up to get started with UP2D8
          </Text>
        </View>

        {/* Signup Form */}
        <GlassCard style={styles.formCard}>
          {/* Name Input */}
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
              Name
            </Text>
            <Input
              value={name}
              onChangeText={(text) => {
                setName(text);
                if (nameError) validateName(text);
              }}
              placeholder="Your name"
              autoCapitalize="words"
              autoComplete="name"
              leftIcon={<User size={20} color={theme.colors.textSecondary} />}
              error={nameError}
            />
          </View>

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
                if (confirmPassword && confirmPasswordError) {
                  validateConfirmPassword(confirmPassword);
                }
              }}
              placeholder="Create a password"
              secureTextEntry
              leftIcon={<Lock size={20} color={theme.colors.textSecondary} />}
              error={passwordError}
            />
          </View>

          {/* Confirm Password Input */}
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
              Confirm Password
            </Text>
            <Input
              value={confirmPassword}
              onChangeText={(text) => {
                setConfirmPassword(text);
                if (confirmPasswordError) validateConfirmPassword(text);
              }}
              placeholder="Confirm your password"
              secureTextEntry
              leftIcon={<Lock size={20} color={theme.colors.textSecondary} />}
              error={confirmPasswordError}
            />
          </View>

          {/* Signup Button */}
          <GlassButton
            onPress={handleSignup}
            loading={isLoading}
            disabled={isLoading}
            size="lg"
            style={styles.signupButton}>
            Create Account
          </GlassButton>

          {/* Info Text */}
          <View
            style={[
              styles.infoBox,
              {
                backgroundColor: theme.colors.primary + '10',
                borderRadius: theme.borderRadius.md,
              },
            ]}>
            <AlertCircle size={16} color={theme.colors.primary} />
            <Text
              style={[
                styles.infoText,
                {
                  color: theme.colors.textSecondary,
                  fontSize: theme.typography.fontSize.xs,
                },
              ]}>
              After signup, you can link your Microsoft account for single sign-on
            </Text>
          </View>
        </GlassCard>

        {/* Login Link */}
        <View style={styles.footer}>
          <Text
            style={[
              styles.footerText,
              {
                color: theme.colors.textSecondary,
                fontSize: theme.typography.fontSize.sm,
              },
            ]}>
            Already have an account?{' '}
          </Text>
          <Pressable onPress={handleLogin} disabled={isLoading}>
            <Text
              style={[
                styles.linkText,
                {
                  color: theme.colors.primary,
                  fontSize: theme.typography.fontSize.sm,
                  fontWeight: theme.typography.fontWeight.semibold,
                },
              ]}>
              Sign In
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
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    marginBottom: 8,
  },
  signupButton: {
    marginTop: 8,
    marginBottom: 12,
  },
  infoBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 12,
    gap: 8,
  },
  infoText: {
    flex: 1,
    lineHeight: 18,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  footerText: {},
  linkText: {},
});
