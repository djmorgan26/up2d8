import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { GlassCard } from '../components/GlassCard';
import { GlassButton } from '../components/GlassButton';
import Icon from 'react-native-vector-icons/Ionicons';
import LinearGradient from 'react-native-linear-gradient';
import { colors, spacing, typography, borderRadius } from '../theme/tokens';
import { AVAILABLE_TOPICS } from '../types';
import { createUser, isValidEmail } from '../services/userService';
import { useUserStore } from '../store/userStore';
import { setOnboardingCompleted } from '../services/storageService';

interface TopicSelectionScreenProps {
  onComplete: () => void;
}

const TopicSelectionScreen: React.FC<TopicSelectionScreenProps> = ({ onComplete }) => {
  const { theme } = useTheme();
  const { setUser } = useUserStore();

  const [email, setEmail] = useState('');
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [newsletterStyle, setNewsletterStyle] = useState<'concise' | 'detailed'>('concise');
  const [isLoading, setIsLoading] = useState(false);
  const [emailError, setEmailError] = useState('');

  // Topic icons mapping
  const topicIcons: { [key: string]: string } = {
    Technology: 'laptop-outline',
    AI: 'bulb-outline',
    Science: 'flask-outline',
    Business: 'briefcase-outline',
    Health: 'fitness-outline',
    Design: 'color-palette-outline',
    Education: 'school-outline',
    Politics: 'megaphone-outline',
    Environment: 'leaf-outline',
    Sports: 'football-outline',
  };

  const topicColors: { [key: string]: string } = {
    Technology: colors.primary[500],
    AI: colors.accent[500],
    Science: colors.primary[600],
    Business: colors.accent[600],
    Health: colors.primary[400],
    Design: colors.accent[400],
    Education: colors.primary[700],
    Politics: colors.accent[700],
    Environment: colors.primary[300],
    Sports: colors.accent[300],
  };

  const toggleTopic = (topic: string) => {
    if (selectedTopics.includes(topic)) {
      setSelectedTopics(selectedTopics.filter(t => t !== topic));
    } else {
      setSelectedTopics([...selectedTopics, topic]);
    }
  };

  const handleContinue = async () => {
    // Validation
    if (!email.trim()) {
      setEmailError('Email is required');
      return;
    }

    if (!isValidEmail(email)) {
      setEmailError('Please enter a valid email address');
      return;
    }

    if (selectedTopics.length === 0) {
      Alert.alert('Select Topics', 'Please select at least one topic to continue');
      return;
    }

    setIsLoading(true);
    setEmailError('');

    try {
      // Create user via API
      const response = await createUser(email.trim(), selectedTopics);

      // Save user to store
      await setUser({
        user_id: response.user_id,
        email: email.trim(),
        topics: selectedTopics,
        created_at: new Date().toISOString(),
        preferences: {
          newsletter_style: newsletterStyle,
        },
      });

      // Mark onboarding as completed
      await setOnboardingCompleted(true);

      // Navigate to main app
      onComplete();
    } catch (error: any) {
      console.error('Error creating user:', error);
      Alert.alert(
        'Subscription Failed',
        error.message || 'Unable to subscribe. Please try again.',
        [{ text: 'OK' }]
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
        <LinearGradient
          colors={[theme.colors.accent, theme.colors.background]}
          style={styles.gradientBackground}
        />

        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* Header */}
          <View style={styles.header}>
            <Text style={[styles.title, { color: theme.colors.textPrimary }]}>
              What interests you?
            </Text>
            <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
              Select topics to personalize your news digest
            </Text>
          </View>

          {/* Topics Grid */}
          <View style={styles.topicsGrid}>
            {AVAILABLE_TOPICS.map((topic) => {
              const isSelected = selectedTopics.includes(topic);
              return (
                <TouchableOpacity
                  key={topic}
                  onPress={() => toggleTopic(topic)}
                  activeOpacity={0.7}
                >
                  <GlassCard
                    style={[
                      styles.topicCard,
                      isSelected && styles.topicCardSelected,
                      { borderColor: isSelected ? topicColors[topic] : 'transparent' },
                    ]}
                    blurIntensity={isSelected ? 'heavy' : 'medium'}
                  >
                    <View
                      style={[
                        styles.topicIcon,
                        {
                          backgroundColor: isSelected
                            ? topicColors[topic]
                            : theme.colors.surface,
                        },
                      ]}
                    >
                      <Icon
                        name={topicIcons[topic] || 'star-outline'}
                        size={24}
                        color={isSelected ? 'white' : theme.colors.textSecondary}
                      />
                    </View>
                    <Text
                      style={[
                        styles.topicName,
                        {
                          color: isSelected
                            ? theme.colors.textPrimary
                            : theme.colors.textSecondary,
                        },
                      ]}
                    >
                      {topic}
                    </Text>
                    {isSelected && (
                      <View style={[styles.checkmark, { backgroundColor: topicColors[topic] }]}>
                        <Icon name="checkmark" size={16} color="white" />
                      </View>
                    )}
                  </GlassCard>
                </TouchableOpacity>
              );
            })}
          </View>

          {/* Email Input */}
          <GlassCard style={styles.emailSection}>
            <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>
              Your Email
            </Text>
            <Text style={[styles.sectionSubtitle, { color: theme.colors.textSecondary }]}>
              We'll send your daily digest here
            </Text>
            <View
              style={[
                styles.inputContainer,
                {
                  backgroundColor: theme.colors.surface,
                  borderColor: emailError ? colors.error : 'transparent',
                },
              ]}
            >
              <Icon name="mail-outline" size={20} color={theme.colors.textSecondary} />
              <TextInput
                style={[styles.input, { color: theme.colors.textPrimary }]}
                placeholder="your@email.com"
                placeholderTextColor={theme.colors.textSecondary}
                value={email}
                onChangeText={(text) => {
                  setEmail(text);
                  setEmailError('');
                }}
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
              />
            </View>
            {emailError ? (
              <Text style={[styles.errorText, { color: colors.error }]}>
                {emailError}
              </Text>
            ) : null}
          </GlassCard>

          {/* Newsletter Style */}
          <GlassCard style={styles.styleSection}>
            <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>
              Newsletter Style
            </Text>
            <View style={styles.styleOptions}>
              <TouchableOpacity
                style={[
                  styles.styleOption,
                  {
                    backgroundColor:
                      newsletterStyle === 'concise'
                        ? theme.colors.primary
                        : theme.colors.surface,
                  },
                ]}
                onPress={() => setNewsletterStyle('concise')}
              >
                <Icon
                  name="flash-outline"
                  size={24}
                  color={newsletterStyle === 'concise' ? 'white' : theme.colors.textSecondary}
                />
                <Text
                  style={[
                    styles.styleOptionText,
                    {
                      color:
                        newsletterStyle === 'concise'
                          ? 'white'
                          : theme.colors.textPrimary,
                    },
                  ]}
                >
                  Concise
                </Text>
                <Text
                  style={[
                    styles.styleOptionDescription,
                    {
                      color:
                        newsletterStyle === 'concise'
                          ? 'rgba(255,255,255,0.8)'
                          : theme.colors.textSecondary,
                    },
                  ]}
                >
                  Quick headlines
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[
                  styles.styleOption,
                  {
                    backgroundColor:
                      newsletterStyle === 'detailed'
                        ? theme.colors.primary
                        : theme.colors.surface,
                  },
                ]}
                onPress={() => setNewsletterStyle('detailed')}
              >
                <Icon
                  name="document-text-outline"
                  size={24}
                  color={newsletterStyle === 'detailed' ? 'white' : theme.colors.textSecondary}
                />
                <Text
                  style={[
                    styles.styleOptionText,
                    {
                      color:
                        newsletterStyle === 'detailed'
                          ? 'white'
                          : theme.colors.textPrimary,
                    },
                  ]}
                >
                  Detailed
                </Text>
                <Text
                  style={[
                    styles.styleOptionDescription,
                    {
                      color:
                        newsletterStyle === 'detailed'
                          ? 'rgba(255,255,255,0.8)'
                          : theme.colors.textSecondary,
                    },
                  ]}
                >
                  Full summaries
                </Text>
              </TouchableOpacity>
            </View>
          </GlassCard>

          {/* Continue Button */}
          <GlassButton
            onPress={handleContinue}
            variant="primary"
            size="lg"
            style={styles.continueButton}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="white" />
            ) : (
              <View style={styles.buttonContent}>
                <Text style={styles.buttonText}>
                  Continue to UP2D8
                </Text>
                <Icon name="arrow-forward" size={20} color="white" />
              </View>
            )}
          </GlassButton>

          {/* Selected count */}
          {selectedTopics.length > 0 && (
            <Text style={[styles.selectionCount, { color: theme.colors.textSecondary }]}>
              {selectedTopics.length} {selectedTopics.length === 1 ? 'topic' : 'topics'} selected
            </Text>
          )}
        </ScrollView>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradientBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 300,
    opacity: 0.1,
  },
  scrollContent: {
    padding: spacing[6],
    paddingBottom: spacing[12],
  },
  header: {
    marginTop: spacing[8],
    marginBottom: spacing[8],
  },
  title: {
    fontSize: typography.fontSize['4xl'],
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[2],
  },
  subtitle: {
    fontSize: typography.fontSize.base,
    lineHeight: typography.fontSize.base * 1.5,
  },
  topicsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: spacing[6],
  },
  topicCard: {
    width: '48%',
    marginBottom: spacing[3],
    padding: spacing[4],
    alignItems: 'center',
    borderWidth: 2,
    position: 'relative',
  },
  topicCardSelected: {
    borderWidth: 2,
  },
  topicIcon: {
    width: 48,
    height: 48,
    borderRadius: borderRadius.xl,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing[2],
  },
  topicName: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold as any,
    textAlign: 'center',
  },
  checkmark: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 24,
    height: 24,
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emailSection: {
    padding: spacing[5],
    marginBottom: spacing[4],
  },
  sectionTitle: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[1],
  },
  sectionSubtitle: {
    fontSize: typography.fontSize.sm,
    marginBottom: spacing[4],
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing[4],
    borderRadius: borderRadius.lg,
    borderWidth: 1,
  },
  input: {
    flex: 1,
    marginLeft: spacing[3],
    fontSize: typography.fontSize.base,
  },
  errorText: {
    fontSize: typography.fontSize.sm,
    marginTop: spacing[2],
  },
  styleSection: {
    padding: spacing[5],
    marginBottom: spacing[6],
  },
  styleOptions: {
    flexDirection: 'row',
    gap: spacing[3],
  },
  styleOption: {
    flex: 1,
    padding: spacing[4],
    borderRadius: borderRadius.lg,
    alignItems: 'center',
  },
  styleOptionText: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.semibold as any,
    marginTop: spacing[2],
  },
  styleOptionDescription: {
    fontSize: typography.fontSize.xs,
    marginTop: spacing[1],
  },
  continueButton: {
    marginBottom: spacing[3],
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing[2],
  },
  buttonText: {
    color: 'white',
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold as any,
  },
  selectionCount: {
    fontSize: typography.fontSize.sm,
    textAlign: 'center',
  },
});

export default TopicSelectionScreen;
