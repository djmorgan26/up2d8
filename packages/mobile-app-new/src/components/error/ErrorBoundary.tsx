/**
 * Error Boundary
 * Catches React errors and shows fallback UI
 */

import React, {Component, ErrorInfo, ReactNode} from 'react';
import {View, Text, StyleSheet, ScrollView} from 'react-native';
import {GlassCard, GlassButton} from '@components/ui';
import {AlertTriangle, RefreshCw} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';

interface Props {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });

    // TODO: Log to error tracking service (Sentry, etc.)
    // logErrorToService(error, errorInfo);
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback provided
      if (this.props.fallback) {
        return this.props.fallback(this.state.error!, this.resetError);
      }

      // Default fallback UI
      return (
        <View style={styles.container}>
          <ScrollView
            contentContainerStyle={styles.content}
            showsVerticalScrollIndicator={false}>
            {/* Error Icon */}
            <LinearGradient
              colors={['#EF4444', '#DC2626']}
              start={{x: 0, y: 0}}
              end={{x: 1, y: 1}}
              style={styles.iconContainer}>
              <AlertTriangle size={48} color="#FFFFFF" />
            </LinearGradient>

            {/* Error Message */}
            <Text style={styles.title}>Oops! Something went wrong</Text>
            <Text style={styles.message}>
              We encountered an unexpected error. Don't worry, we've logged it and will
              fix it soon.
            </Text>

            {/* Error Details Card (Dev only) */}
            {__DEV__ && this.state.error && (
              <GlassCard style={styles.errorCard}>
                <Text style={styles.errorTitle}>Error Details (Dev Mode)</Text>
                <Text style={styles.errorText}>{this.state.error.toString()}</Text>
                {this.state.errorInfo && (
                  <ScrollView style={styles.stackTrace} nestedScrollEnabled>
                    <Text style={styles.stackText}>
                      {this.state.errorInfo.componentStack}
                    </Text>
                  </ScrollView>
                )}
              </GlassCard>
            )}

            {/* Actions */}
            <View style={styles.actions}>
              <GlassButton
                onPress={this.resetError}
                icon={<RefreshCw size={20} color="#FFFFFF" />}
                iconPosition="left"
                size="lg">
                Try Again
              </GlassButton>
            </View>
          </ScrollView>
        </View>
      );
    }

    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F0F14',
  },
  content: {
    flexGrow: 1,
    padding: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 12,
  },
  message: {
    fontSize: 16,
    color: '#9CA3AF',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
    paddingHorizontal: 16,
  },
  errorCard: {
    width: '100%',
    padding: 16,
    marginBottom: 24,
  },
  errorTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#EF4444',
    marginBottom: 8,
  },
  errorText: {
    fontSize: 12,
    color: '#F87171',
    fontFamily: 'Courier',
    marginBottom: 12,
  },
  stackTrace: {
    maxHeight: 200,
    backgroundColor: '#1F2937',
    borderRadius: 8,
    padding: 8,
  },
  stackText: {
    fontSize: 10,
    color: '#9CA3AF',
    fontFamily: 'Courier',
  },
  actions: {
    width: '100%',
    gap: 12,
  },
});

export default ErrorBoundary;
