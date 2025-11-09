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
}

const Feeds = () => {
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [loading, setLoading] = useState(true);
  const [newFeedUrl, setNewFeedUrl] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
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
      await addRSSFeed(newFeedUrl);
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

      <div className="space-y-4">
        {loading ? (
          <>
            {[...Array(4)].map((_, i) => (
              <FeedSkeleton key={i} />
            ))}
          </>
        ) : feeds.length === 0 ? (
          <GlassCard className="text-center py-12">
            <p className="text-muted-foreground">No feeds added yet. Add your first feed to get started!</p>
          </GlassCard>
        ) : (
          feeds.map((feed) => (
            <GlassCard key={feed.id} hover>
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-foreground truncate">
                    {feed.title || "Untitled Feed"}
                  </h3>
                  <p className="text-sm text-muted-foreground truncate">{feed.url}</p>
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
          ))
        )}
      </div>
    </div>
  );
};

export default Feeds;
