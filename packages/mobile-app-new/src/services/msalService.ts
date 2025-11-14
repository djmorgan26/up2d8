/**
 * MSAL Service
 * Microsoft Entra ID authentication service for React Native
 *
 * NOTE: This uses @azure/msal-react-native for authentication
 * See: https://github.com/AzureAD/microsoft-authentication-library-for-react-native
 */

import {msalConfig, validateMSALConfig, getMSALAuthority} from '@config/msalConfig';

// MSAL types
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

// Type for MSAL client (will be loaded dynamically)
interface MSALClientType {
  createPublicClientApplication: (config: any) => Promise<any>;
}

/**
 * MSAL Service class
 * Handles Microsoft Entra ID authentication
 */
class MSALService {
  private isConfigured = false;
  private msalClient: any = null;
  private initPromise: Promise<void> | null = null;

  constructor() {
    this.isConfigured = validateMSALConfig();
  }

  /**
   * Initialize MSAL client (lazy)
   */
  private async initialize(): Promise<void> {
    if (this.msalClient) {
      return;
    }

    if (this.initPromise) {
      return this.initPromise;
    }

    this.initPromise = (async () => {
      try {
        // Dynamically import MSAL to avoid errors if not configured
        const MSALModule = await import('@azure/msal-react-native');

        const config = {
          auth: {
            clientId: msalConfig.clientId,
            authority: getMSALAuthority(),
          },
          cache: {
            cacheLocation: 'secureStore', // Use secure storage
          },
        };

        this.msalClient = await MSALModule.createPublicClientApplication(config);
        console.log('MSAL client initialized successfully');
      } catch (error: any) {
        console.error('MSAL initialization failed:', error);
        throw new Error('Failed to initialize MSAL: ' + error.message);
      }
    })();

    return this.initPromise;
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
      await this.initialize();

      const params = {
        scopes: msalConfig.scopes,
      };

      const result = await this.msalClient.acquireToken(params);

      return {
        accessToken: result.accessToken,
        idToken: result.idToken,
        account: {
          username: result.account.username,
          name: result.account.name || result.account.username,
          homeAccountId: result.account.homeAccountId,
          localAccountId: result.account.localAccountId,
        },
        expiresOn: result.expiresOn,
      };
    } catch (error: any) {
      console.error('MSAL acquireTokenInteractive failed:', error);

      // Check if user cancelled
      if (error.message?.includes('cancel') || error.message?.includes('Cancel')) {
        throw new Error('Sign in was cancelled');
      }

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
      await this.initialize();

      const params = {
        scopes: msalConfig.scopes,
        account: account,
      };

      const result = await this.msalClient.acquireTokenSilent(params);

      return {
        accessToken: result.accessToken,
        idToken: result.idToken,
        account: {
          username: result.account.username,
          name: result.account.name || result.account.username,
          homeAccountId: result.account.homeAccountId,
          localAccountId: result.account.localAccountId,
        },
        expiresOn: result.expiresOn,
      };
    } catch (error: any) {
      console.error('MSAL acquireTokenSilent failed:', error);
      // If silent acquisition fails, caller should fall back to interactive
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
      await this.initialize();

      const accounts = await this.msalClient.getAllAccounts();

      return accounts.map((acc: any) => ({
        username: acc.username,
        name: acc.name || acc.username,
        homeAccountId: acc.homeAccountId,
        localAccountId: acc.localAccountId,
      }));
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
      await this.initialize();

      if (account) {
        await this.msalClient.removeAccount(account);
      } else {
        // Sign out all accounts
        const accounts = await this.getAccounts();
        for (const acc of accounts) {
          await this.msalClient.removeAccount(acc);
        }
      }

      console.log('MSAL sign out successful');
    } catch (error) {
      console.error('MSAL signOut failed:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const msalService = new MSALService();

// Export types
export type {MSALAccount, MSALAuthResult};
