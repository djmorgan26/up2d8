import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { AuthProvider } from "./auth/AuthProvider";
import { registerServiceWorker } from "./registerServiceWorker";

// Register service worker for PWA functionality
registerServiceWorker();

createRoot(document.getElementById("root")!).render(
  <AuthProvider>
    <App />
  </AuthProvider>
);
