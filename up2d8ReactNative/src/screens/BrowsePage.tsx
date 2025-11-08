import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import Icon from 'react-native-vector-icons/Ionicons';
import { GlassCard } from '../components/GlassCard';
import { colors, spacing, typography, borderRadius } from '../theme/tokens';

const categories = [
  { id: 1, name: 'Technology', icon: 'laptop-outline', color: colors.primary[500] },
  { id: 2, name: 'Design', icon: 'color-palette-outline', color: colors.accent[500] },
  { id: 3, name: 'Business', icon: 'briefcase-outline', color: colors.primary[600] },
  { id: 4, name: 'Health', icon: 'fitness-outline', color: colors.accent[600] },
  { id: 5, name: 'Science', icon: 'flask-outline', color: colors.primary[700] },
  { id: 6, name: 'Education', icon: 'school-outline', color: colors.accent[400] },
];

const BrowsePage: React.FC = () => {
  const { theme } = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Gradient Background */}
      <View style={styles.gradientContainer}>
        <View
          style={[
            styles.gradient,
            {
              backgroundColor: theme.colors.accent,
              opacity: 0.1,
            },
          ]}
        />
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header Section */}
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.colors.textPrimary }]}>
            Discover
          </Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            Explore topics that interest you
          </Text>
        </View>

        {/* Categories Grid */}
        <View style={styles.grid}>
          {categories.map((category) => (
            <GlassCard
              key={category.id}
              style={styles.categoryCard}
              blurIntensity="medium"
            >
              <View style={[styles.iconContainer, { backgroundColor: category.color }]}>
                <Icon name={category.icon} size={32} color="white" />
              </View>
              <Text style={[styles.categoryName, { color: theme.colors.textPrimary }]}>
                {category.name}
              </Text>
            </GlassCard>
          ))}
        </View>

        {/* Featured Content */}
        <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>
          Featured Content
        </Text>

        <GlassCard style={styles.featuredCard}>
          <View style={[styles.featuredImage, { backgroundColor: colors.primary[300] }]}>
            <Icon name="rocket-outline" size={48} color="white" />
          </View>
          <Text style={[styles.featuredTitle, { color: theme.colors.textPrimary }]}>
            Getting Started Guide
          </Text>
          <Text style={[styles.featuredDescription, { color: theme.colors.textSecondary }]}>
            Learn the basics and unlock powerful features to enhance your experience.
          </Text>
        </GlassCard>

        <GlassCard style={styles.featuredCard}>
          <View style={[styles.featuredImage, { backgroundColor: colors.accent[300] }]}>
            <Icon name="star-outline" size={48} color="white" />
          </View>
          <Text style={[styles.featuredTitle, { color: theme.colors.textPrimary }]}>
            Premium Features
          </Text>
          <Text style={[styles.featuredDescription, { color: theme.colors.textSecondary }]}>
            Discover exclusive content and advanced tools for premium members.
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
    overflow: 'hidden',
  },
  gradient: {
    flex: 1,
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
  },
  title: {
    fontSize: typography.fontSize['4xl'],
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[2],
  },
  subtitle: {
    fontSize: typography.fontSize.base,
    fontWeight: typography.fontWeight.regular as any,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -spacing[2],
    marginBottom: spacing[6],
  },
  categoryCard: {
    width: '47%',
    margin: spacing[2],
    alignItems: 'center',
    paddingVertical: spacing[6],
  },
  iconContainer: {
    width: 64,
    height: 64,
    borderRadius: borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing[3],
  },
  categoryName: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold as any,
  },
  sectionTitle: {
    fontSize: typography.fontSize['2xl'],
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[4],
  },
  featuredCard: {
    marginBottom: spacing[4],
  },
  featuredImage: {
    width: '100%',
    height: 120,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing[3],
  },
  featuredTitle: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold as any,
    marginBottom: spacing[2],
  },
  featuredDescription: {
    fontSize: typography.fontSize.sm,
    lineHeight: typography.lineHeight.relaxed * typography.fontSize.sm,
  },
});

export default BrowsePage;
