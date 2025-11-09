import { useEffect, useState } from "react";
import { getRSSFeeds, addRSSFeed, deleteRSSFeed, suggestRSSFeeds } from "@/lib/api";
import { GlassCard } from "@/components/GlassCard";
import { FeedSkeleton } from "@/components/LoadingSkeleton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Rss, Trash2, Plus, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useMsal } from "@azure/msal-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { loginRequest } from "@/config/msalConfig";

interface Feed {
  id: string;
  url: string;
  title?: string;
  category?: string; // Add category
}

interface SuggestedFeed {
  title: string;
  url: string;
  category: string;
}

const Feeds = () => {
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [loading, setLoading] = useState(true);
  const [newFeedUrl, setNewFeedUrl] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState(""); // New state for search term
  const [llmSearchQuery, setLlmSearchQuery] = useState(""); // State for LLM search query
  const [llmSuggestions, setLlmSuggestions] = useState<SuggestedFeed[]>([]); // State for LLM suggestions
  const [llmLoading, setLlmLoading] = useState(false); // State for LLM loading
  const { instance, accounts } = useMsal();
  const isAuthenticated = accounts.length > 0;

  const fetchFeeds = async () => {
    try {
      const response = await getRSSFeeds();
      setFeeds(response.data.data);
    } catch (error) {
      console.error("Failed to fetch feeds:", error);
      toast.error("Failed to load feeds");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeeds();
  }, []);

  const handleAddFeed = async () => {
    if (!isAuthenticated) {
      try {
        await instance.loginPopup(loginRequest);
      } catch (error) {
        console.error("Login failed:", error);
        return;
      }
    }

    if (!newFeedUrl.trim()) {
      toast.error("Please enter a feed URL");
      return;
    }

    try {
      await addRSSFeed(newFeedUrl); // Backend supports category, but not exposed in UI yet
      toast.success("Feed added successfully");
      setNewFeedUrl("");
      setDialogOpen(false);
      fetchFeeds();
    } catch (error) {
      console.error("Failed to add feed:", error);
      toast.error("Failed to add feed");
    }
  };

  const handleSuggestFeeds = async () => {
    if (!isAuthenticated) {
      try {
        await instance.loginPopup(loginRequest);
      } catch (error) {
        console.error("Login failed:", error);
        return;
      }
    }

    if (!llmSearchQuery.trim()) {
      toast.error("Please enter a search query for suggestions");
      return;
    }

    setLlmLoading(true);
    setLlmSuggestions([]); // Clear previous suggestions
    try {
      const response = await suggestRSSFeeds(llmSearchQuery);
      setLlmSuggestions(response.data.suggestions);
      if (response.data.suggestions.length === 0) {
        toast.info("No suggestions found for your query.");
      }
    } catch (error) {
      console.error("Failed to get feed suggestions:", error);
      toast.error("Failed to get feed suggestions");
    } finally {
      setLlmLoading(false);
    }
  };

  const handleAddSuggestedFeed = async (url: string, category: string, title: string) => {
    if (!isAuthenticated) {
      try {
        await instance.loginPopup(loginRequest);
      } catch (error) {
        console.error("Login failed:", error);
        return;
      }
    }

    try {
      await addRSSFeed(url, category, title);
      toast.success("Feed added successfully");
      setLlmSuggestions(llmSuggestions.filter(feed => feed.url !== url)); // Remove from suggestions
      fetchFeeds();
    } catch (error) {
      console.error("Failed to add suggested feed:", error);
      toast.error("Failed to add suggested feed");
    }
  };

  const handleDeleteFeed = async (feedId: string) => {
    if (!isAuthenticated) {
      try {
        await instance.loginPopup(loginRequest);
      } catch (error) {
        console.error("Login failed:", error);
        return;
      }
    }

    try {
      await deleteRSSFeed(feedId);
      toast.success("Feed deleted successfully");
      fetchFeeds();
    } catch (error) {
      console.error("Failed to delete feed:", error);
      toast.error("Failed to delete feed");
    }
  };

  // Filter feeds based on search term
  const filteredFeeds = feeds.filter(
    (feed) =>
      feed.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      feed.url.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Group filtered feeds by category
  const groupedFeeds = filteredFeeds.reduce((acc, feed) => {
    const category = feed.category || "Uncategorized";
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(feed);
    return acc;
  }, {} as Record<string, Feed[]>);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 md:h-12 md:w-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
            <Rss className="h-5 w-5 md:h-6 md:w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">RSS Feeds</h1>
            <p className="text-sm text-muted-foreground hidden md:block">Manage your content sources</p>
          </div>
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gradient-primary text-white shadow-lg">
              <Plus className="mr-2 h-4 w-4" />
              Add Feed
            </Button>
          </DialogTrigger>
          <DialogContent className="glass-card border-0">
            <DialogHeader>
              <DialogTitle>Add New RSS Feed</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Add by URL</h3>
              <Input
                placeholder="Enter RSS feed URL"
                value={newFeedUrl}
                onChange={(e) => setNewFeedUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddFeed()}
                className="glass-card border-border/50"
              />
              <Button onClick={handleAddFeed} className="w-full gradient-primary text-white">
                Add Feed
              </Button>

              <div className="relative flex items-center py-5">
                <div className="flex-grow border-t border-gray-400"></div>
                <span className="flex-shrink mx-4 text-gray-400">OR</span>
                <div className="flex-grow border-t border-gray-400"></div>
              </div>

              <h3 className="text-lg font-semibold">Suggest Feeds with AI</h3>
              <div className="flex space-x-2">
                <Input
                  placeholder="e.g., 'tech news', 'cooking blogs'"
                  value={llmSearchQuery}
                  onChange={(e) => setLlmSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSuggestFeeds()}
                  className="glass-card border-border/50"
                />
                <Button onClick={handleSuggestFeeds} disabled={llmLoading} className="gradient-primary text-white">
                  {llmLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Suggest"}
                </Button>
              </div>

              {llmSuggestions.length > 0 && (
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {llmSuggestions.map((sugg, index) => (
                    <GlassCard key={index} hover className="flex items-center justify-between p-3">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{sugg.title}</p>
                        <p className="text-sm text-muted-foreground truncate">{sugg.url}</p>
                        <p className="text-xs text-muted-foreground">Category: {sugg.category}</p>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => handleAddSuggestedFeed(sugg.url, sugg.category, sugg.title)}
                        className="ml-2 shrink-0 gradient-primary text-white"
                      >
                        Add
                      </Button>
                    </GlassCard>
                  ))}
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search Input */}
      <Input
        placeholder="Search feeds by title or URL..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="glass-card border-border/50"
      />

      <div className="space-y-4">
        {loading ? (
          <>
            {[...Array(4)].map((_, i) => (
              <FeedSkeleton key={i} />
            ))}
          </>
        ) : Object.keys(groupedFeeds).length === 0 ? (
          <GlassCard className="text-center py-12">
            <p className="text-muted-foreground">No feeds found. Try adjusting your search or add a new feed!</p>
          </GlassCard>
        ) : (
          Object.entries(groupedFeeds).map(([category, categoryFeeds]) => (
            <div key={category} className="space-y-3">
              <h2 className="text-xl font-semibold text-foreground mt-6">{category}</h2>
              {categoryFeeds.map((feed) => (
                <GlassCard key={feed.id} hover>
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-foreground truncate">
                        {feed.title || "Untitled Feed"}
                      </h3>
                      <p className="text-sm text-muted-foreground truncate">
                        <a href={feed.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                          {feed.url}
                        </a>
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteFeed(feed.id)}
                      className="shrink-0 text-destructive hover:text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </GlassCard>
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Feeds;
