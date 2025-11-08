import React, { useRef, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Animated } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import Icon from 'react-native-vector-icons/Ionicons';
import { GlassCard } from '../components/GlassCard';
import { GlassButton } from '../components/GlassButton';
import {
  colors,
  spacing,
  typography,
  borderRadius,
  shadows,
} from '../theme/tokens';
import LinearGradient from 'react-native-linear-gradient';

const plans = [
  {
    id: 1,
    name: 'Basic',
    price: 'Free',
    features: [
      'Access to basic features',
      'Limited storage',
      'Community support',
    ],
    icon: 'gift-outline',
    color: colors.neutral[500],
    isPopular: false,
  },
  {
    id: 2,
    name: 'Pro',
    price: '$9.99/mo',
    features: [
      'All basic features',
      'Unlimited storage',
      'Priority support',
      'Advanced analytics',
    ],
    icon: 'star-outline',
    color: colors.primary[500],
    isPopular: true,
  },
  {
    id: 3,
    name: 'Enterprise',
    price: '$29.99/mo',
    features: [
      'All Pro features',
      'Custom integrations',
      'Dedicated account manager',
      '24/7 premium support',
    ],
    icon: 'rocket-outline',
    color: colors.accent[500],
    isPopular: false,
  },
];

const PlanCard = ({ plan, theme }) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (plan.isPopular) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(scaleAnim, {
            toValue: 1.02,
            duration: 1500,
            useNativeDriver: true,
          }),
          Animated.timing(scaleAnim, {
            toValue: 1,
            duration: 1500,
            useNativeDriver: true,
          }),
        ]),
      ).start();
    }
  }, [plan.isPopular, scaleAnim]);

  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <GlassCard
        style={[styles.planCard, plan.isPopular && styles.popularCard]}
        blurIntensity={plan.isPopular ? 'heavy' : 'medium'}
      >
        {plan.isPopular && (
          <View
            style={[
              styles.popularBadge,
              { backgroundColor: theme.colors.primary },
            ]}
          >
            <Text style={styles.popularText}>Most Popular</Text>
          </View>
        )}

        <View style={[styles.planIcon, { backgroundColor: plan.color }]}>
          <Icon name={plan.icon} size={40} color="white" />
        </View>

        <Text style={[styles.planName, { color: theme.colors.textPrimary }]}>
          {plan.name}
        </Text>

        <Text style={[styles.planPrice, { color: theme.colors.primary }]}>
          {plan.price}
        </Text>

        <View style={styles.featuresContainer}>
          {plan.features.map((feature, index) => (
            <View key={index} style={styles.featureRow}>
              <Icon name="checkmark-circle" size={20} color={plan.color} />
              <Text
                style={[
                  styles.featureText,
                  { color: theme.colors.textSecondary },
                ]}
              >
                {feature}
              </Text>
            </View>
          ))}
        </View>

        <GlassButton
          onPress={() => console.log(`Subscribe to ${plan.name}`)}
          variant={plan.isPopular ? 'primary' : 'secondary'}
          fullWidth
          style={styles.subscribeButton}
        >
          {plan.price === 'Free' ? 'Current Plan' : 'Subscribe Now'}
        </GlassButton>
      </GlassCard>
    </Animated.View>
  );
};

const SubscribePage: React.FC = () => {
  const { theme } = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <LinearGradient
        colors={[colors.primary[700], theme.colors.background]}
        style={styles.gradientContainer}
      />

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.colors.textPrimary }]}>
            Choose Your Plan
          </Text>
          <Text
            style={[styles.subtitle, { color: theme.colors.textSecondary }]}
          >
            Unlock premium features and take your experience to the next level
          </Text>
        </View>

        {plans.map((plan) => (
          <PlanCard key={plan.id} plan={plan} theme={theme} />
        ))}

        <GlassCard style={styles.infoCard}>
          <Icon
            name="information-circle-outline"
            size={32}
            color={theme.colors.info}
          />
          <Text style={[styles.infoTitle, { color: theme.colors.textPrimary }]}>
            30-Day Money-Back Guarantee
          </Text>
          <Text style={[styles.infoText, { color: theme.colors.textSecondary }]}>
            Try any plan risk-free. If you're not satisfied, get a full refund
            within 30 days.
          </Text>
        </GlassCard>
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
    opacity: 0.15,
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
    alignItems: 'center',
  },
  title: {
    fontSize: typography.fontSize['4xl'],
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[2],
    textAlign: 'center',
  },
  subtitle: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.regular as any,
    textAlign: 'center',
    paddingHorizontal: spacing[4],
  },
  planCard: {
    marginBottom: spacing[4],
    alignItems: 'center',
    paddingVertical: spacing[6],
    position: 'relative',
  },
  popularCard: {
    borderWidth: 2,
    borderColor: colors.primary[500],
    ...shadows.lg,
  },
  popularBadge: {
    position: 'absolute',
    top: -12,
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[1],
    borderRadius: borderRadius.full,
  },
  popularText: {
    color: 'white',
    fontSize: typography.fontSize.xs,
    fontWeight: typography.fontWeight.bold as any,
    textTransform: 'uppercase',
  },
  planIcon: {
    width: 80,
    height: 80,
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing[4],
    ...shadows.md,
  },
  planName: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[2],
  },
  planPrice: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: typography.fontWeight.heavy as any,
    marginBottom: spacing[5],
  },
  featuresContainer: {
    width: '100%',
    marginBottom: spacing[5],
  },
  featureRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing[2],
    paddingHorizontal: spacing[2],
  },
  featureText: {
    fontSize: typography.fontSize.sm,
    marginLeft: spacing[2],
    flex: 1,
  },
  subscribeButton: {
    marginTop: spacing[2],
  },
  infoCard: {
    alignItems: 'center',
    paddingVertical: spacing[6],
  },
  infoTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.bold as any,
    marginTop: spacing[3],
    marginBottom: spacing[2],
    textAlign: 'center',
  },
  infoText: {
    fontSize: typography.fontSize.sm,
    textAlign: 'center',
    lineHeight: typography.lineHeight.relaxed * typography.fontSize.sm,
  },
});

export default SubscribePage;
