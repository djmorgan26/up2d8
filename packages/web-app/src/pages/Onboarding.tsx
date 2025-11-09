import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GlassCard } from "@/components/GlassCard";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Sparkles } from "lucide-react";
import { toast } from "sonner";
import { useMsal } from "@azure/msal-react";

const topics = [
  { id: "technology", label: "Technology" },
  { id: "business", label: "Business" },
  { id: "science", label: "Science" },
  { id: "health", label: "Health" },
  { id: "sports", label: "Sports" },
  { id: "entertainment", label: "Entertainment" },
  { id: "politics", label: "Politics" },
  { id: "world", label: "World News" },
];

const Onboarding = () => {
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const navigate = useNavigate();
  const { accounts } = useMsal();

  const toggleTopic = (topicId: string) => {
    setSelectedTopics((prev) =>
      prev.includes(topicId)
        ? prev.filter((id) => id !== topicId)
        : [...prev, topicId]
    );
  };

  const handleSubmit = async () => {
    if (selectedTopics.length === 0) {
      toast.error("Please select at least one topic");
      return;
    }

    try {
      // TODO: Send preferences to backend
      // await updateUser(accounts[0].localAccountId, { preferences: selectedTopics });
      
      toast.success("Welcome to up2d8! 🎉");
      navigate("/");
    } catch (error) {
      console.error("Failed to save preferences:", error);
      toast.error("Failed to save preferences");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900 p-6">
      <GlassCard className="max-w-2xl w-full animate-fade-in">
        <div className="text-center mb-8">
          <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center mx-auto mb-4 shadow-xl">
            <Sparkles className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Welcome to up2d8!</h1>
          <p className="text-muted-foreground">
            Let's personalize your news experience. Select the topics you're interested in.
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
          {topics.map((topic) => (
            <div
              key={topic.id}
              onClick={() => toggleTopic(topic.id)}
              className={`glass-card p-4 rounded-lg cursor-pointer transition-all duration-200 hover:shadow-lg ${
                selectedTopics.includes(topic.id)
                  ? "ring-2 ring-primary bg-primary/10"
                  : ""
              }`}
            >
              <div className="flex items-center gap-3">
                <Checkbox
                  checked={selectedTopics.includes(topic.id)}
                  onCheckedChange={() => toggleTopic(topic.id)}
                />
                <span className="text-sm font-medium">{topic.label}</span>
              </div>
            </div>
          ))}
        </div>

        <Button
          onClick={handleSubmit}
          className="w-full gradient-primary text-white shadow-lg text-lg py-6"
          disabled={selectedTopics.length === 0}
        >
          Get Started
        </Button>
      </GlassCard>
    </div>
  );
};

export default Onboarding;
