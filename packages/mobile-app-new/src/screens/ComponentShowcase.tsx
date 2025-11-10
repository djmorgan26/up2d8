/**
 * Component Showcase
 * Demo screen showing all UI components
 * Temporary screen for Phase 2 testing
 */

import React, {useState} from 'react';
import {View, Text, ScrollView, StyleSheet, Alert} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {GlassCard, GlassButton, Input, Avatar, Badge, Skeleton} from '@components/ui';
import {Search, Mail, User} from 'lucide-react-native';

export default function ComponentShowcase() {
  const {theme, toggleTheme, isDark} = useTheme();
  const [inputValue, setInputValue] = useState('');

  return (
    <View style={[styles.container, {backgroundColor: theme.colors.background}]}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text
            style={[
              styles.title,
              {
                color: theme.colors.textPrimary,
                fontSize: theme.typography.fontSize['4xl'],
                fontWeight: theme.typography.fontWeight.bold,
              },
            ]}>
            Components
          </Text>
          <Text
            style={[
              styles.subtitle,
              {
                color: theme.colors.textSecondary,
                fontSize: theme.typography.fontSize.base,
              },
            ]}>
            Phase 2 Component Showcase
          </Text>
        </View>

        {/* Theme Toggle */}
        <GlassCard style={styles.section}>
          <Text style={[styles.sectionTitle, {color: theme.colors.textPrimary}]}>
            Theme
          </Text>
          <GlassButton onPress={toggleTheme}>
            {isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          </GlassButton>
        </GlassCard>

        {/* Buttons */}
        <GlassCard style={styles.section}>
          <Text style={[styles.sectionTitle, {color: theme.colors.textPrimary}]}>
            Buttons
          </Text>
          <View style={styles.row}>
            <GlassButton
              variant="default"
              onPress={() => Alert.alert('Button', 'Default pressed')}>
              Default
            </GlassButton>
          </View>
          <View style={styles.row}>
            <GlassButton variant="outline" onPress={() => Alert.alert('Button', 'Outline')}>
              Outline
            </GlassButton>
          </View>
          <View style={styles.row}>
            <GlassButton variant="ghost" onPress={() => Alert.alert('Button', 'Ghost')}>
              Ghost
            </GlassButton>
          </View>
          <View style={styles.row}>
            <GlassButton variant="destructive" onPress={() => Alert.alert('Delete', 'Are you sure?')}>
              Destructive
            </GlassButton>
          </View>
          <View style={styles.row}>
            <GlassButton
              size="sm"
              onPress={() => Alert.alert('Button', 'Small')}
              style={{marginRight: 8}}>
              Small
            </GlassButton>
            <GlassButton size="lg" onPress={() => Alert.alert('Button', 'Large')}>
              Large
            </GlassButton>
          </View>
          <View style={styles.row}>
            <GlassButton loading>Loading...</GlassButton>
          </View>
          <View style={styles.row}>
            <GlassButton disabled>Disabled</GlassButton>
          </View>
        </GlassCard>

        {/* Inputs */}
        <GlassCard style={styles.section}>
          <Text style={[styles.sectionTitle, {color: theme.colors.textPrimary}]}>
            Inputs
          </Text>
          <Input
            label="Email"
            placeholder="Enter your email"
            value={inputValue}
            onChangeText={setInputValue}
            keyboardType="email-address"
            autoCapitalize="none"
            leftIcon={<Mail size={20} color={theme.colors.textSecondary} />}
          />
          <Input
            label="Password"
            placeholder="Enter your password"
            secureTextEntry
          />
          <Input
            label="Search"
            placeholder="Search..."
            leftIcon={<Search size={20} color={theme.colors.textSecondary} />}
          />
          <Input
            label="With Error"
            placeholder="This has an error"
            error="This field is required"
          />
          <Input label="Disabled" placeholder="Disabled input" editable={false} />
        </GlassCard>

        {/* Avatars */}
        <GlassCard style={styles.section}>
          <Text style={[styles.sectionTitle, {color: theme.colors.textPrimary}]}>
            Avatars
          </Text>
          <View style={styles.row}>
            <Avatar name="John Doe" size="sm" style={{marginRight: 8}} />
            <Avatar name="Jane Smith" size="md" style={{marginRight: 8}} />
            <Avatar name="Bob Johnson" size="lg" style={{marginRight: 8}} />
            <Avatar name="Alice Williams" size="xl" />
          </View>
        </GlassCard>

        {/* Badges */}
        <GlassCard style={styles.section}>
          <Text style={[styles.sectionTitle, {color: theme.colors.textPrimary}]}>
            Badges
          </Text>
          <View style={styles.row}>
            <Badge variant="default" style={{marginRight: 8}}>
              Default
            </Badge>
            <Badge variant="primary" style={{marginRight: 8}}>
              Primary
            </Badge>
            <Badge variant="success" style={{marginRight: 8}}>
              Success
            </Badge>
          </View>
          <View style={styles.row}>
            <Badge variant="warning" style={{marginRight: 8}}>
              Warning
            </Badge>
            <Badge variant="error" style={{marginRight: 8}}>
              Error
            </Badge>
            <Badge variant="outline">Outline</Badge>
          </View>
        </GlassCard>

        {/* Skeletons */}
        <GlassCard style={styles.section}>
          <Text style={[styles.sectionTitle, {color: theme.colors.textPrimary}]}>
            Skeleton Loaders
          </Text>
          <Skeleton height={20} style={{marginBottom: 8}} />
          <Skeleton height={40} width="80%" style={{marginBottom: 8}} />
          <Skeleton height={60} borderRadius={theme.borderRadius.lg} />
        </GlassCard>

        {/* Glass Cards */}
        <GlassCard style={styles.section}>
          <Text style={[styles.sectionTitle, {color: theme.colors.textPrimary}]}>
            Glass Cards
          </Text>
          <Text style={[styles.text, {color: theme.colors.textSecondary}]}>
            This is a GlassCard with glassmorphism effect. It has a blur background on
            iOS and a semi-transparent background on Android.
          </Text>
        </GlassCard>

        <GlassCard pressable onPress={() => Alert.alert('Card', 'Pressable card tapped')} style={styles.section}>
          <Text style={[styles.sectionTitle, {color: theme.colors.textPrimary}]}>
            Pressable Card
          </Text>
          <Text style={[styles.text, {color: theme.colors.textSecondary}]}>
            This card is pressable. Tap it to see the press animation!
          </Text>
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
    marginBottom: 24,
  },
  title: {
    marginBottom: 4,
  },
  subtitle: {
    marginTop: 4,
  },
  section: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
  },
  text: {
    fontSize: 14,
    lineHeight: 20,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
});
