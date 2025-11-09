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
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
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

    // Add user message
    const newMessage = { role: "user", content: message };
    setMessages([...messages, newMessage]);
    setMessage("");

    // TODO: Integrate with backend API
    toast.info("Chat integration coming soon!");
  };

  return (
    <div className="space-y-6 animate-fade-in h-[calc(100vh-8rem)] flex flex-col">
      <div className="flex items-center gap-3">
        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
          <MessageSquare className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-foreground">Chat</h1>
          <p className="text-muted-foreground">Ask questions about your news</p>
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
            messages.map((msg, idx) => (
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
                </div>
              </div>
            ))
          )}
        </div>

        <div className="flex gap-2">
          <Input
            placeholder={
              isAuthenticated
                ? "Type your message..."
                : "Log in to send messages..."
            }
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
            disabled={!isAuthenticated}
            className="glass-card border-border/50"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!isAuthenticated || !message.trim()}
            className="gradient-primary text-white shadow-lg shrink-0"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </GlassCard>
    </div>
  );
};

export default Chat;
