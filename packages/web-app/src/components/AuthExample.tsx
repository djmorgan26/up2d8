import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

/**
 * Example component demonstrating Entra ID authentication.
 *
 * Usage:
 * 1. Add this component to your app to test authentication
 * 2. Click "Login" to authenticate with Microsoft
 * 3. Click "Test Protected API" to call a protected backend endpoint
 */
export const AuthExample = () => {
  const { isAuthenticated, user, login, logout, getAccessToken } = useAuth();
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    try {
      setError(null);
      await login();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  const handleLogout = async () => {
    try {
      setError(null);
      await logout();
      setApiResponse(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Logout failed');
    }
  };

  const testProtectedAPI = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = await getAccessToken();
      if (!token) {
        setError('No access token available');
        return;
      }

      // Call backend protected endpoint
      const response = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.statusText}`);
      }

      const data = await response.json();
      setApiResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'API call failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h2>Entra ID Authentication Example</h2>

      <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
        <h3>Authentication Status</h3>
        <p>
          <strong>Status:</strong> {isAuthenticated ? '✅ Authenticated' : '❌ Not Authenticated'}
        </p>

        {isAuthenticated && user && (
          <div>
            <p><strong>User Info:</strong></p>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li>Name: {user.name || 'N/A'}</li>
              <li>Email: {user.username || 'N/A'}</li>
              <li>User ID: {user.localAccountId || 'N/A'}</li>
            </ul>
          </div>
        )}

        <div style={{ marginTop: '15px' }}>
          {!isAuthenticated ? (
            <button
              onClick={handleLogin}
              style={{
                padding: '10px 20px',
                backgroundColor: '#0078d4',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Login with Microsoft
            </button>
          ) : (
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={handleLogout}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#d13438',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Logout
              </button>

              <button
                onClick={testProtectedAPI}
                disabled={loading}
                style={{
                  padding: '10px 20px',
                  backgroundColor: loading ? '#ccc' : '#107c10',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                }}
              >
                {loading ? 'Loading...' : 'Test Protected API'}
              </button>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div
          style={{
            marginTop: '20px',
            padding: '15px',
            backgroundColor: '#fde7e9',
            color: '#a80000',
            borderRadius: '8px',
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}

      {apiResponse && (
        <div
          style={{
            marginTop: '20px',
            padding: '15px',
            backgroundColor: '#dff6dd',
            borderRadius: '8px',
          }}
        >
          <h3>API Response</h3>
          <pre style={{ overflow: 'auto' }}>
            {JSON.stringify(apiResponse, null, 2)}
          </pre>
        </div>
      )}

      <div style={{ marginTop: '30px', fontSize: '14px', color: '#666' }}>
        <h4>How to use authentication in your components:</h4>
        <pre style={{ backgroundColor: '#f5f5f5', padding: '10px', borderRadius: '4px', overflow: 'auto' }}>
{`import { useAuth } from './hooks/useAuth';

function MyComponent() {
  const { isAuthenticated, user, getAccessToken } = useAuth();

  const callAPI = async () => {
    const token = await getAccessToken();
    const response = await fetch('/api/endpoint', {
      headers: { 'Authorization': \`Bearer \${token}\` }
    });
    // Handle response...
  };

  return (
    <div>
      {isAuthenticated ? (
        <p>Welcome, {user.name}!</p>
      ) : (
        <p>Please login</p>
      )}
    </div>
  );
}`}
        </pre>
      </div>
    </div>
  );
};
