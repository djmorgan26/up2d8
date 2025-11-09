import { Configuration, PopupRequest } from '@azure/msal-browser';

// MSAL configuration
export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_APP_ENTRA_CLIENT_ID || '',
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_APP_ENTRA_TENANT_ID}`,
    redirectUri: import.meta.env.VITE_APP_ENTRA_REDIRECT_URI || window.location.origin,
  },
  cache: {
    cacheLocation: 'localStorage', // Use localStorage for persistence
    storeAuthStateInCookie: false, // Set to true for IE 11 or Edge
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) return;
        switch (level) {
          case 0: // Error
            console.error(message);
            break;
          case 1: // Warning
            console.warn(message);
            break;
          case 2: // Info
            console.info(message);
            break;
          case 3: // Verbose
            console.debug(message);
            break;
        }
      },
    },
  },
};

// Add scopes for access token request
export const loginRequest: PopupRequest = {
  scopes: [import.meta.env.VITE_APP_ENTRA_API_SCOPE || 'User.Read'],
};

// Add scopes for silent token request
export const tokenRequest = {
  scopes: [import.meta.env.VITE_APP_ENTRA_API_SCOPE || 'User.Read'],
};
