import { useState } from "react";
import { GlassCard } from "@/components/GlassCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MessageSquare, Send } from "lucide-react";
import { useMsal } from "@azure/msal-react";
import { loginRequest } from "@/config/msalConfig";
import { toast } from "sonner";

const Chat = () => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<
    Array<{
      role: string;
      content: string;
      sources?: Array<{ web: { uri: string; title: string } }>;
    }>
  >([]);
  const [isLoading, setIsLoading] = useState(false);
  const { instance, accounts } = useMsal();
  const isAuthenticated = accounts.length > 0;

  const handleSendMessage = async () => {
    if (!isAuthenticated) {
      try {
        await instance.loginPopup(loginRequest);
      } catch (error) {
        console.error("Login failed:", error);
        return;
      }
    }

    if (!message.trim()) return;

    const userMessage = { role: "user", content: message };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setMessage("");
    setIsLoading(true);

    try {
      const accessToken = await instance.acquireTokenSilent({
        ...loginRequest,
        account: accounts[0],
      });

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken.accessToken}`,
        },
        body: JSON.stringify({ prompt: message }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response from assistant");
      }

      const data = await response.json();
      const assistantMessage = {
        role: "assistant",
        content: data.reply || data.text,
        sources: data.sources,
      };
      setMessages([...newMessages, assistantMessage]);
    } catch (error) {
      console.error("Chat API error:", error);
      toast.error("Sorry, something went wrong. Please try again.");
      // Optional: Revert optimistic UI update on error
      setMessages(messages);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in h-[calc(100vh-8rem)] flex flex-col">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 md:h-12 md:w-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
          <MessageSquare className="h-5 w-5 md:h-6 md:w-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-foreground">Chat</h1>
          <p className="text-sm text-muted-foreground hidden md:block">Ask questions about your news</p>
        </div>
      </div>

      <GlassCard className="flex-1 flex flex-col min-h-0">
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center text-center">
              <div>
                <MessageSquare className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Start a conversation by asking questions about your news feed
                </p>
                {!isAuthenticated && (
                  <p className="text-sm text-muted-foreground mt-2">
                    Please log in to send messages
                  </p>
                )}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg p-3 ${
                      msg.role === "user"
                        ? "gradient-primary text-white"
                        : "bg-muted text-foreground"
                    }`}
                  >
                    {msg.content}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-border/50">
                        <p className="text-xs font-semibold text-muted-foreground mb-1">Sources:</p>
                        <div className="space-y-1">
                          {msg.sources.map((source, sourceIdx) => (
                            <a
                              key={sourceIdx}
                              href={source.web.uri}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-1 text-xs text-primary hover:underline"
                              title={source.web.title} // Tooltip on hover
                            >
                              <MessageSquare className="h-3 w-3 shrink-0" />
                              <span className="truncate">{source.web.title}</span>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="max-w-[70%] rounded-lg p-3 bg-muted text-foreground">
                    <div className="flex gap-1 items-center">
                      <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }}></div>
                      <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }}></div>
                      <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }}></div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        <div className="flex gap-2">
          <Input
            placeholder={
              isLoading
                ? "Waiting for response..."
                : isAuthenticated
                ? "Type your message..."
                : "Log in to send messages..."
            }
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !isLoading && handleSendMessage()}
            disabled={!isAuthenticated || isLoading}
            className="glass-card border-border/50"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!isAuthenticated || !message.trim() || isLoading}
            className="gradient-primary text-white shadow-lg shrink-0"
          >
            <Send className={`h-4 w-4 ${isLoading ? "animate-pulse" : ""}`} />
          </Button>
        </div>
      </GlassCard>
    </div>
  );
};

export default Chat;
