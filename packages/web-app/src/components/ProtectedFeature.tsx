import { ReactNode } from "react";
import { useMsal } from "@azure/msal-react";
import { Button } from "./ui/button";
import { GlassCard } from "./GlassCard";
import { Lock } from "lucide-react";
import { loginRequest } from "@/config/msalConfig";

interface ProtectedFeatureProps {
  children: ReactNode;
  message?: string;
}

export const ProtectedFeature = ({
  children,
  message = "Please log in to access this feature",
}: ProtectedFeatureProps) => {
  const { instance, accounts } = useMsal();
  const isAuthenticated = accounts.length > 0;

  const handleLogin = async () => {
    try {
      await instance.loginPopup(loginRequest);
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  if (!isAuthenticated) {
    return (
      <GlassCard className="text-center py-12">
        <Lock className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-lg font-semibold mb-2">{message}</h3>
        <p className="text-sm text-muted-foreground mb-6">
          Sign in with your Microsoft account to continue
        </p>
        <Button onClick={handleLogin} className="gradient-primary text-white">
          Login to Continue
        </Button>
      </GlassCard>
    );
  }

  return <>{children}</>;
};
