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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Badge } from "@/components/ui/badge";
import { X, Sparkles, Plus } from "lucide-react";
import { toast } from "sonner";
import { updateUser, suggestTopics } from "@/lib/api";

interface PreferencesDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  userId?: string;
  currentTopics?: string[];
  currentNewsletterFormat?: "concise" | "detailed";
  onSaveSuccess?: () => void;
}

export function PreferencesDialog({
  open,
  onOpenChange,
  userId,
  currentTopics = [],
  currentNewsletterFormat = "concise",
  onSaveSuccess,
}: PreferencesDialogProps) {
  const [topics, setTopics] = useState<string[]>(currentTopics);
  const [newTopic, setNewTopic] = useState("");
  const [newsletterFormat, setNewsletterFormat] = useState<"concise" | "detailed">(
    currentNewsletterFormat
  );
  const [saving, setSaving] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const handleAddTopic = () => {
    if (newTopic.trim() && !topics.includes(newTopic.trim())) {
      setTopics([...topics, newTopic.trim()]);
      setNewTopic("");
    }
  };

  const handleRemoveTopic = (topic: string) => {
    setTopics(topics.filter((t) => t !== topic));
  };

  const handleGetSuggestions = async () => {
    setLoadingSuggestions(true);
    try {
      const response = await suggestTopics(topics, searchQuery);
      const newSuggestions = response.data.suggestions.filter(
        (s: string) => !topics.includes(s)
      );
      setSuggestions(newSuggestions);
      if (newSuggestions.length === 0) {
        toast.info("No new topic suggestions found");
      }
    } catch (error) {
      console.error("Failed to get topic suggestions:", error);
      toast.error("Failed to get topic suggestions");
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleAddSuggestion = (suggestion: string) => {
    if (!topics.includes(suggestion)) {
      setTopics([...topics, suggestion]);
      setSuggestions(suggestions.filter((s) => s !== suggestion));
    }
  };

  const handleSave = async () => {
    if (!userId) {
      toast.error("User not authenticated");
      return;
    }

    if (topics.length === 0) {
      toast.error("Please add at least one topic");
      return;
    }

    setSaving(true);
    try {
      await updateUser(userId, {
        topics,
        preferences: { newsletter_format: newsletterFormat },
      });
      toast.success("Preferences saved successfully!");
      if (onSaveSuccess) {
        onSaveSuccess();
      }
      onOpenChange(false);
    } catch (error) {
      console.error("Failed to save preferences:", error);
      toast.error("Failed to save preferences");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Edit Preferences</DialogTitle>
          <DialogDescription>
            Customize your news feed topics and newsletter format
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Topics Section */}
          <div className="space-y-3">
            <Label htmlFor="topics">Topics of Interest</Label>
            <div className="flex gap-2">
              <Input
                id="topics"
                placeholder="Add a topic..."
                value={newTopic}
                onChange={(e) => setNewTopic(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleAddTopic()}
              />
              <Button type="button" onClick={handleAddTopic}>
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-2 min-h-[40px]">
              {topics.map((topic) => (
                <Badge
                  key={topic}
                  variant="secondary"
                  className="gap-1 px-3 py-1"
                >
                  {topic}
                  <button
                    onClick={() => handleRemoveTopic(topic)}
                    className="ml-1 hover:text-destructive"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
              {topics.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  No topics added yet
                </p>
              )}
            </div>
          </div>

          {/* Topic Suggestions */}
          <div className="space-y-3 border-t pt-4">
            <Label>Discover New Topics</Label>
            <div className="flex gap-2">
              <Input
                placeholder="Search for topic ideas..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleGetSuggestions()}
              />
              <Button
                type="button"
                variant="outline"
                onClick={handleGetSuggestions}
                disabled={loadingSuggestions}
              >
                <Sparkles className="h-4 w-4 mr-2" />
                {loadingSuggestions ? "Loading..." : "Suggest"}
              </Button>
            </div>
            {suggestions.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {suggestions.map((suggestion) => (
                  <Badge
                    key={suggestion}
                    variant="outline"
                    className="gap-1 px-3 py-1 cursor-pointer hover:bg-primary/10"
                    onClick={() => handleAddSuggestion(suggestion)}
                  >
                    <Plus className="h-3 w-3" />
                    {suggestion}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Newsletter Format Section */}
          <div className="space-y-3">
            <Label>Newsletter Format</Label>
            <RadioGroup
              value={newsletterFormat}
              onValueChange={(value) =>
                setNewsletterFormat(value as "concise" | "detailed")
              }
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="concise" id="concise" />
                <Label htmlFor="concise" className="font-normal cursor-pointer">
                  Concise - Quick summaries and headlines
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="detailed" id="detailed" />
                <Label htmlFor="detailed" className="font-normal cursor-pointer">
                  Detailed - In-depth analysis and full articles
                </Label>
              </div>
            </RadioGroup>
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
