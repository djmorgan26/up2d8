/**
 * MSAL Service
 * Microsoft Entra ID authentication service for React Native
 *
 * NOTE: This requires @azure/msal-react-native to be properly configured
 * See: https://github.com/AzureAD/microsoft-authentication-library-for-react-native
 */

import {msalConfig, validateMSALConfig, getMSALAuthority} from '@config/msalConfig';

// Placeholder types until MSAL is fully integrated
interface MSALAccount {
  username: string;
  name: string;
  homeAccountId: string;
  localAccountId: string;
}

interface MSALAuthResult {
  accessToken: string;
  idToken: string;
  account: MSALAccount;
  expiresOn: number;
}

/**
 * MSAL Service class
 * Handles Microsoft Entra ID authentication
 */
class MSALService {
  private isConfigured = false;

  constructor() {
    this.isConfigured = validateMSALConfig();
  }

  /**
   * Check if MSAL is properly configured
   */
  isReady(): boolean {
    return this.isConfigured;
  }

  /**
   * Acquire token interactively (opens browser)
   *
   * @returns Promise with auth result including access token
   */
  async acquireTokenInteractive(): Promise<MSALAuthResult> {
    if (!this.isConfigured) {
      throw new Error('MSAL not configured. Please set ENTRA_CLIENT_ID in .env');
    }

    try {
      // TODO: Implement actual MSAL React Native flow
      //
      // Example implementation:
      //
      // import { MSALClient } from '@azure/msal-react-native';
      //
      // const msalClient = new MSALClient({
      //   auth: {
      //     clientId: msalConfig.clientId,
      //     authority: getMSALAuthority(),
      //     redirectUri: msalConfig.redirectUri,
      //   },
      // });
      //
      // const result = await msalClient.acquireTokenInteractive({
      //   scopes: msalConfig.scopes,
      // });
      //
      // return result;

      throw new Error('MSAL interactive login not yet implemented. Please complete MSAL integration.');
    } catch (error: any) {
      console.error('MSAL acquireTokenInteractive failed:', error);
      throw new Error(error.message || 'Failed to acquire token interactively');
    }
  }

  /**
   * Acquire token silently (from cache)
   *
   * @param account The account to acquire token for
   * @returns Promise with auth result including access token
   */
  async acquireTokenSilent(account: MSALAccount): Promise<MSALAuthResult> {
    if (!this.isConfigured) {
      throw new Error('MSAL not configured');
    }

    try {
      // TODO: Implement actual MSAL React Native silent token acquisition
      //
      // const result = await msalClient.acquireTokenSilent({
      //   scopes: msalConfig.scopes,
      //   account: account,
      // });
      //
      // return result;

      throw new Error('MSAL silent token acquisition not yet implemented');
    } catch (error: any) {
      console.error('MSAL acquireTokenSilent failed:', error);
      // If silent acquisition fails, fall back to interactive
      throw error;
    }
  }

  /**
   * Get all cached accounts
   *
   * @returns Promise with array of cached accounts
   */
  async getAccounts(): Promise<MSALAccount[]> {
    if (!this.isConfigured) {
      return [];
    }

    try {
      // TODO: Implement actual MSAL React Native get accounts
      //
      // const accounts = await msalClient.getAccounts();
      // return accounts;

      return [];
    } catch (error) {
      console.error('MSAL getAccounts failed:', error);
      return [];
    }
  }

  /**
   * Sign out
   *
   * @param account The account to sign out (optional, signs out all if not provided)
   */
  async signOut(account?: MSALAccount): Promise<void> {
    if (!this.isConfigured) {
      return;
    }

    try {
      // TODO: Implement actual MSAL React Native sign out
      //
      // if (account) {
      //   await msalClient.removeAccount(account);
      // } else {
      //   const accounts = await msalClient.getAccounts();
      //   for (const acc of accounts) {
      //     await msalClient.removeAccount(acc);
      //   }
      // }

      console.log('MSAL signOut called (not yet implemented)');
    } catch (error) {
      console.error('MSAL signOut failed:', error);
    }
  }
}

// Export singleton instance
export const msalService = new MSALService();

// Export types
export type {MSALAccount, MSALAuthResult};
