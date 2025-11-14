/**
 * MSAL Configuration for React Native
 * Microsoft Entra ID authentication setup
 */

import {Platform} from 'react-native';

export interface MSALConfig {
  clientId: string;
  tenantId: string;
  redirectUri: string;
  scopes: string[];
}

// Load from environment variables
// Note: React Native uses different env var loading than web
// You may need react-native-config or similar
const ENTRA_CLIENT_ID = process.env.ENTRA_CLIENT_ID || '';
const ENTRA_TENANT_ID = process.env.ENTRA_TENANT_ID || 'common';
const ENTRA_REDIRECT_URI = process.env.ENTRA_REDIRECT_URI || 'msauth.com.up2d8.mobile://auth';
const ENTRA_API_SCOPE = process.env.ENTRA_API_SCOPE || 'User.Read';

export const msalConfig: MSALConfig = {
  clientId: ENTRA_CLIENT_ID,
  tenantId: ENTRA_TENANT_ID,
  redirectUri: ENTRA_REDIRECT_URI,
  scopes: [ENTRA_API_SCOPE],
};

/**
 * Validate MSAL configuration
 */
export const validateMSALConfig = (): boolean => {
  if (!msalConfig.clientId) {
    console.warn('MSAL: clientId not configured');
    return false;
  }
  return true;
};

/**
 * Get MSAL authority URL
 */
export const getMSALAuthority = (): string => {
  return `https://login.microsoftonline.com/${msalConfig.tenantId}`;
};
