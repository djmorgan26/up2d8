import { ProtectedFeature } from "@/components/ProtectedFeature";
import { GlassCard } from "@/components/GlassCard";
import { Button } from "@/components/ui/button";
import { Settings as SettingsIcon, Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

const Settings = () => {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null;
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.classList.toggle("dark", savedTheme === "dark");
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.classList.toggle("dark", newTheme === "dark");
    toast.success(`Theme changed to ${newTheme} mode`);
  };

  const handleEditPreferences = () => {
    toast.info("Preferences editor coming soon!");
  };

  const handleConfigureNotifications = () => {
    toast.info("Notification settings coming soon!");
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-3">
        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
          <SettingsIcon className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground">Manage your preferences</p>
        </div>
      </div>

      <ProtectedFeature message="Please log in to access settings">
        <div className="space-y-4">
          <GlassCard>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-1">Theme</h3>
                <p className="text-sm text-muted-foreground">
                  Choose between light and dark mode
                </p>
              </div>
              <Button
                onClick={toggleTheme}
                className="gradient-primary text-white shadow-lg"
                size="lg"
              >
                {theme === "light" ? (
                  <>
                    <Moon className="mr-2 h-4 w-4" />
                    Dark Mode
                  </>
                ) : (
                  <>
                    <Sun className="mr-2 h-4 w-4" />
                    Light Mode
                  </>
                )}
              </Button>
            </div>
          </GlassCard>

          <GlassCard>
            <div>
              <h3 className="text-lg font-semibold mb-1">Preferences</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Customize your news feed preferences
              </p>
              <Button
                variant="outline"
                className="glass-card border-border/50"
                onClick={handleEditPreferences}
              >
                Edit Preferences
              </Button>
            </div>
          </GlassCard>

          <GlassCard>
            <div>
              <h3 className="text-lg font-semibold mb-1">Notifications</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Manage how you receive updates
              </p>
              <Button
                variant="outline"
                className="glass-card border-border/50"
                onClick={handleConfigureNotifications}
              >
                Configure Notifications
              </Button>
            </div>
          </GlassCard>
        </div>
      </ProtectedFeature>
    </div>
  );
};

export default Settings;
