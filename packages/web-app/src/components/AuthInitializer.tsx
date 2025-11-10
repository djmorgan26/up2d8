import { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { setTokenGetter, getUser } from '@/lib/api';
import { useNavigate, useLocation } from 'react-router-dom';

/**
 * AuthInitializer component that:
 * 1. Sets up automatic token fetching for all API requests
 * 2. Checks if user has completed onboarding
 * 3. Redirects to onboarding if needed
 */
export const AuthInitializer = () => {
  const { isAuthenticated, getAccessToken } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Set up token getter once on mount
  useEffect(() => {
    setTokenGetter(getAccessToken);
  }, [getAccessToken]);

  useEffect(() => {
    const checkOnboarding = async () => {
      if (isAuthenticated && location.pathname !== '/onboarding') {
        try {
          // Pass a dummy user ID since backend uses the token
          await getUser('me');
          // User exists, they've completed onboarding
        } catch (error: any) {
          // If user not found (404), redirect to onboarding
          if (error.response?.status === 404) {
            console.log('User not found, redirecting to onboarding');
            navigate('/onboarding');
          }
        }
      }
    };

    checkOnboarding();
  }, [isAuthenticated, getAccessToken, navigate, location.pathname]);

  return null;
};
