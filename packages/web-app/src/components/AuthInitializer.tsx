import { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { setAuthToken, getUser } from '@/lib/api';
import { useNavigate, useLocation } from 'react-router-dom';

/**
 * AuthInitializer component that:
 * 1. Sets the auth token on the API client when user is authenticated
 * 2. Checks if user has completed onboarding
 * 3. Redirects to onboarding if needed
 */
export const AuthInitializer = () => {
  const { isAuthenticated, getAccessToken } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const initializeAuth = async () => {
      if (isAuthenticated) {
        try {
          // Get and set the access token
          const token = await getAccessToken();
          if (token) {
            setAuthToken(token);

            // Check if user has completed onboarding (only if not already on onboarding page)
            if (location.pathname !== '/onboarding') {
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
          }
        } catch (error) {
          console.error('Failed to initialize auth:', error);
        }
      } else {
        // Clear token if not authenticated
        setAuthToken(null);
      }
    };

    initializeAuth();
  }, [isAuthenticated, getAccessToken, navigate, location.pathname]);

  return null;
};
