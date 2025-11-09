import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { toast } from "sonner";
import { updateUser } from "@/lib/api";

interface NotificationsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  userId?: string;
  currentSettings?: {
    emailNotifications?: boolean;
    newsletterFrequency?: "daily" | "weekly" | "monthly";
    breakingNews?: boolean;
  };
  onSaveSuccess?: () => void;
}

export function NotificationsDialog({
  open,
  onOpenChange,
  userId,
  currentSettings = {},
  onSaveSuccess,
}: NotificationsDialogProps) {
  const [emailNotifications, setEmailNotifications] = useState(
    currentSettings.emailNotifications ?? true
  );
  const [newsletterFrequency, setNewsletterFrequency] = useState<
    "daily" | "weekly" | "monthly"
  >(currentSettings.newsletterFrequency ?? "daily");
  const [breakingNews, setBreakingNews] = useState(
    currentSettings.breakingNews ?? false
  );
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!userId) {
      toast.error("User not authenticated");
      return;
    }

    setSaving(true);
    try {
      await updateUser(userId, {
        preferences: {
          email_notifications: emailNotifications,
          newsletter_frequency: newsletterFrequency,
          breaking_news: breakingNews,
        },
      });
      toast.success("Notification settings saved!");
      if (onSaveSuccess) {
        onSaveSuccess();
      }
      onOpenChange(false);
    } catch (error) {
      console.error("Failed to save notification settings:", error);
      toast.error("Failed to save notification settings");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Notification Settings</DialogTitle>
          <DialogDescription>
            Manage how you receive updates and newsletters
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Email Notifications Toggle */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="email-notifications">Email Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Receive email updates for your personalized digest
              </p>
            </div>
            <Switch
              id="email-notifications"
              checked={emailNotifications}
              onCheckedChange={setEmailNotifications}
            />
          </div>

          {/* Newsletter Frequency */}
          <div className="space-y-3">
            <Label>Newsletter Frequency</Label>
            <RadioGroup
              value={newsletterFrequency}
              onValueChange={(value) =>
                setNewsletterFrequency(value as "daily" | "weekly" | "monthly")
              }
              disabled={!emailNotifications}
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="daily" id="daily" />
                <Label
                  htmlFor="daily"
                  className="font-normal cursor-pointer"
                >
                  Daily - Every morning at 8 AM
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="weekly" id="weekly" />
                <Label
                  htmlFor="weekly"
                  className="font-normal cursor-pointer"
                >
                  Weekly - Every Monday morning
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="monthly" id="monthly" />
                <Label
                  htmlFor="monthly"
                  className="font-normal cursor-pointer"
                >
                  Monthly - First of each month
                </Label>
              </div>
            </RadioGroup>
          </div>

          {/* Breaking News Toggle */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="breaking-news">Breaking News Alerts</Label>
              <p className="text-sm text-muted-foreground">
                Get instant notifications for major news events
              </p>
            </div>
            <Switch
              id="breaking-news"
              checked={breakingNews}
              onCheckedChange={setBreakingNews}
              disabled={!emailNotifications}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Save Changes"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
