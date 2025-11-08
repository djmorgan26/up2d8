import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  ScrollView,
} from 'react-native';
import { useTheme } from '../context/ThemeContext';
import { GlassCard } from '../components/GlassCard';
import { GlassButton } from '../components/GlassButton';
import Icon from 'react-native-vector-icons/Ionicons';
import LinearGradient from 'react-native-linear-gradient';
import {
  colors,
  spacing,
  typography,
  borderRadius,
} from '../theme/tokens';

const { width, height } = Dimensions.get('window');

interface WelcomeScreenProps {
  onGetStarted: () => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onGetStarted }) => {
  const { theme } = useTheme();
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      }),
      Animated.spring(slideAnim, {
        toValue: 0,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }),
    ]).start();
  }, [fadeAnim, slideAnim]);

  const features = [
    {
      icon: 'chatbubbles-outline',
      title: 'AI News Assistant',
      description: 'Ask questions and get instant answers powered by Google Gemini with real-time web search',
      color: colors.primary[500],
    },
    {
      icon: 'newspaper-outline',
      title: 'Personalized Digests',
      description: 'Get news tailored to your interests from top sources, filtered just for you',
      color: colors.accent[500],
    },
    {
      icon: 'mail-outline',
      title: 'Daily Newsletters',
      description: 'Wake up to a curated email digest every morning with the stories that matter to you',
      color: colors.primary[600],
    },
  ];

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Animated gradient background */}
      <LinearGradient
        colors={[
          theme.colors.primary,
          theme.colors.accent,
          theme.colors.background,
        ]}
        style={styles.gradientBackground}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <Animated.View
          style={[
            styles.content,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          {/* Logo/Brand Section */}
          <View style={styles.logoSection}>
            <View style={[styles.logoCircle, { backgroundColor: theme.colors.primary }]}>
              <Icon name="newspaper" size={48} color="white" />
            </View>
            <Text style={[styles.brandName, { color: theme.colors.textPrimary }]}>
              UP2D8
            </Text>
            <Text style={[styles.tagline, { color: theme.colors.textSecondary }]}>
              Your Personalized AI News Digest
            </Text>
          </View>

          {/* Features Section */}
          <View style={styles.featuresSection}>
            {features.map((feature, index) => (
              <GlassCard key={index} style={styles.featureCard}>
                <View style={[styles.featureIcon, { backgroundColor: feature.color }]}>
                  <Icon name={feature.icon} size={28} color="white" />
                </View>
                <View style={styles.featureContent}>
                  <Text style={[styles.featureTitle, { color: theme.colors.textPrimary }]}>
                    {feature.title}
                  </Text>
                  <Text style={[styles.featureDescription, { color: theme.colors.textSecondary }]}>
                    {feature.description}
                  </Text>
                </View>
              </GlassCard>
            ))}
          </View>

          {/* Value Proposition */}
          <GlassCard style={styles.valueCard} blurIntensity="heavy">
            <Text style={[styles.valueTitle, { color: theme.colors.textPrimary }]}>
              Stop Missing Important News
            </Text>
            <Text style={[styles.valueText, { color: theme.colors.textSecondary }]}>
              Stay informed without the overwhelm. UP2D8 uses AI to bring you only the news that matters to you, delivered how and when you want it.
            </Text>
          </GlassCard>

          {/* CTA Button */}
          <GlassButton
            onPress={onGetStarted}
            variant="primary"
            size="lg"
            style={styles.ctaButton}
          >
            <View style={styles.buttonContent}>
              <Text style={styles.buttonText}>Get Started</Text>
              <Icon name="arrow-forward" size={20} color="white" />
            </View>
          </GlassButton>

          {/* Footer */}
          <Text style={[styles.footer, { color: theme.colors.textSecondary }]}>
            Free forever • No credit card required
          </Text>
        </Animated.View>
      </ScrollView>
    </View>
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
    height: height * 0.5,
    opacity: 0.15,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: spacing[6],
    paddingBottom: spacing[12],
  },
  content: {
    flex: 1,
    paddingTop: spacing[16],
  },
  logoSection: {
    alignItems: 'center',
    marginBottom: spacing[12],
  },
  logoCircle: {
    width: 96,
    height: 96,
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing[4],
    shadowColor: colors.primary[500],
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  brandName: {
    fontSize: typography.fontSize['5xl'],
    fontWeight: typography.fontWeight.heavy as any,
    letterSpacing: 2,
    marginBottom: spacing[2],
  },
  tagline: {
    fontSize: typography.fontSize.lg,
    textAlign: 'center',
    paddingHorizontal: spacing[4],
  },
  featuresSection: {
    marginBottom: spacing[8],
  },
  featureCard: {
    flexDirection: 'row',
    padding: spacing[4],
    marginBottom: spacing[4],
    alignItems: 'flex-start',
  },
  featureIcon: {
    width: 56,
    height: 56,
    borderRadius: borderRadius.xl,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing[4],
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[1],
  },
  featureDescription: {
    fontSize: typography.fontSize.sm,
    lineHeight: typography.fontSize.sm * 1.5,
  },
  valueCard: {
    padding: spacing[6],
    marginBottom: spacing[8],
    alignItems: 'center',
  },
  valueTitle: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[3],
    textAlign: 'center',
  },
  valueText: {
    fontSize: typography.fontSize.base,
    textAlign: 'center',
    lineHeight: typography.fontSize.base * 1.6,
  },
  ctaButton: {
    marginBottom: spacing[4],
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing[2],
  },
  buttonText: {
    color: 'white',
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold as any,
  },
  footer: {
    fontSize: typography.fontSize.sm,
    textAlign: 'center',
  },
});

export default WelcomeScreen;
