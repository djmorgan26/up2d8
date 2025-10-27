import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader } from 'lucide-react';
import { Button } from '../ui/Button';
import { ChatMessage } from './ChatMessage';
import { useChat } from '../../hooks/useChat';

interface ChatInterfaceProps {
  sessionId: string;
  suggestedQuestions?: string[];
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  sessionId,
  suggestedQuestions = [],
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, isConnected, isLoading, sendMessage } = useChat(sessionId);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !isConnected) return;

    sendMessage(input.trim());
    setInput('');
  };

  const handleSuggestedQuestion = (question: string) => {
    if (!isConnected) return;
    sendMessage(question);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Connection status */}
      {!isConnected && (
        <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-2 text-sm text-yellow-800">
          Connecting to chat...
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <h3 className="text-xl font-semibold text-text-primary mb-2">
              Start a conversation
            </h3>
            <p className="text-text-secondary mb-6">
              Ask me anything about your digest articles
            </p>

            {/* Suggested questions */}
            {suggestedQuestions.length > 0 && (
              <div className="max-w-2xl mx-auto">
                <p className="text-sm text-text-secondary mb-3">Try asking:</p>
                <div className="space-y-2">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestedQuestion(question)}
                      className="w-full text-left px-4 py-3 rounded-xl bg-white border-2 border-border-light hover:border-primary hover:bg-primary-pale transition-all duration-200 text-sm font-medium shadow-sm hover:shadow-md"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            onFollowUpClick={handleSuggestedQuestion}
          />
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex items-center gap-2 text-text-secondary">
            <Loader className="h-4 w-4 animate-spin" />
            <span className="text-sm">Thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-border-light bg-white p-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your digest..."
              disabled={!isConnected}
              className="flex-1 px-4 py-3 rounded-xl border-2 border-border-light focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary disabled:bg-bg-soft disabled:cursor-not-allowed shadow-sm"
            />
            <Button
              type="submit"
              variant="primary"
              disabled={!input.trim() || !isConnected || isLoading}
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
