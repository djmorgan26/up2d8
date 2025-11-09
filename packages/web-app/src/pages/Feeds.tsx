import { useEffect, useState } from "react";
import { getRSSFeeds, addRSSFeed, deleteRSSFeed } from "@/lib/api";
import { GlassCard } from "@/components/GlassCard";
import { FeedSkeleton } from "@/components/LoadingSkeleton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Rss, Trash2, Plus } from "lucide-react";
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

const Feeds = () => {
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [loading, setLoading] = useState(true);
  const [newFeedUrl, setNewFeedUrl] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState(""); // New state for search term
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
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
            <Rss className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">RSS Feeds</h1>
            <p className="text-muted-foreground">Manage your content sources</p>
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
