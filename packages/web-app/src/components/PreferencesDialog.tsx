import { useState, useEffect } from "react";
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
import { Checkbox } from "@/components/ui/checkbox";
import { X, Sparkles, Plus } from "lucide-react";
import { toast } from "sonner";
import { updateUser, suggestTopics } from "@/lib/api";
import { TOPIC_CATEGORIES } from "@/lib/constants";

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
  const [customTopics, setCustomTopics] = useState<string[]>(() => {
    // Filter out predefined topics to get custom ones
    const predefinedIds = TOPIC_CATEGORIES.map(t => t.id);
    return currentTopics.filter(t => !predefinedIds.includes(t));
  });
  const [newTopic, setNewTopic] = useState("");
  const [newsletterFormat, setNewsletterFormat] = useState<"concise" | "detailed">(
    currentNewsletterFormat
  );
  const [saving, setSaving] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Sync state when currentTopics or currentNewsletterFormat changes
  useEffect(() => {
    setTopics(currentTopics);
    const predefinedIds = TOPIC_CATEGORIES.map(t => t.id);
    setCustomTopics(currentTopics.filter(t => !predefinedIds.includes(t)));
    setNewsletterFormat(currentNewsletterFormat);
  }, [currentTopics, currentNewsletterFormat]);

  const togglePredefinedTopic = (topicId: string) => {
    setTopics((prev) =>
      prev.includes(topicId)
        ? prev.filter((id) => id !== topicId)
        : [...prev, topicId]
    );
  };

  const handleAddTopic = () => {
    const trimmedTopic = newTopic.trim();
    if (trimmedTopic && !topics.includes(trimmedTopic)) {
      setTopics([...topics, trimmedTopic]);
      setCustomTopics([...customTopics, trimmedTopic]);
      setNewTopic("");
    }
  };

  const handleRemoveTopic = (topic: string) => {
    setTopics(topics.filter((t) => t !== topic));
    setCustomTopics(customTopics.filter((t) => t !== topic));
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
      // Check if it's a custom topic (not in predefined list)
      const predefinedIds = TOPIC_CATEGORIES.map(t => t.id);
      if (!predefinedIds.includes(suggestion)) {
        setCustomTopics([...customTopics, suggestion]);
      }
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
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Preferences</DialogTitle>
          <DialogDescription>
            Customize your news feed topics and newsletter format
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Predefined Topics Section */}
          <div className="space-y-3">
            <Label>Topic Categories</Label>
            <p className="text-sm text-muted-foreground">
              Select topics you're interested in to personalize your news feed
            </p>
            <div className="grid grid-cols-2 gap-3 max-h-[300px] overflow-y-auto pr-2">
              {TOPIC_CATEGORIES.map((topic) => (
                <div
                  key={topic.id}
                  onClick={() => togglePredefinedTopic(topic.id)}
                  className={`glass-card p-3 rounded-lg cursor-pointer transition-all duration-200 hover:shadow-md ${
                    topics.includes(topic.id)
                      ? "ring-2 ring-primary bg-primary/10"
                      : ""
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <Checkbox
                      checked={topics.includes(topic.id)}
                      onCheckedChange={() => togglePredefinedTopic(topic.id)}
                      className="mt-0.5"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium">{topic.label}</div>
                      <div className="text-xs text-muted-foreground line-clamp-2">
                        {topic.description}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Custom Topics Section */}
          {customTopics.length > 0 && (
            <div className="space-y-3 border-t pt-4">
              <Label>Custom Topics</Label>
              <div className="flex flex-wrap gap-2">
                {customTopics.map((topic) => (
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
              </div>
            </div>
          )}

          {/* Add Custom Topic & AI Suggestions */}
          <div className="space-y-3 border-t pt-4">
            <Label>Add Custom Topic</Label>
            <div className="flex gap-2">
              <Input
                placeholder="Enter a custom topic..."
                value={newTopic}
                onChange={(e) => setNewTopic(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleAddTopic()}
              />
              <Button type="button" onClick={handleAddTopic} disabled={!newTopic.trim()}>
                <Plus className="h-4 w-4 mr-2" />
                Add
              </Button>
            </div>

            {/* AI-Powered Suggestions */}
            <div className="space-y-2 pt-2">
              <div className="flex gap-2">
                <Input
                  placeholder="Search for topic ideas with AI..."
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
                  {loadingSuggestions ? "..." : "AI"}
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
