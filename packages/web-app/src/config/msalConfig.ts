import { Configuration, PopupRequest } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_APP_ENTRA_CLIENT_ID || "",
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_APP_ENTRA_TENANT_ID || "common"}`,
    redirectUri: import.meta.env.VITE_APP_ENTRA_REDIRECT_URI || window.location.origin,
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: false,
  },
};

export const loginRequest: PopupRequest = {
  scopes: [import.meta.env.VITE_APP_ENTRA_API_SCOPE || "User.Read"],
};
