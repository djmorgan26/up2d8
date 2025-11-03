
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Message as MessageType, Role } from '../types';
import { askGeminiWithSearch } from '../services/geminiService';
import { Message } from './Message';
import { ChatInput } from './ChatInput';

export const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<MessageType[]>([
    { id: 'initial-1', role: Role.MODEL, text: "Hello! I'm your UP2D8 news assistant. Tell me what industry, company, or topic you're interested in, and I'll find the latest information for you." }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messageListRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = useCallback(async (prompt: string) => {
    if (!prompt.trim() || isLoading) return;

    const userMessage: MessageType = {
      id: `user-${Date.now()}`,
      role: Role.USER,
      text: prompt,
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const { text, sources } = await askGeminiWithSearch(prompt);
      const modelMessage: MessageType = {
        id: `model-${Date.now()}`,
        role: Role.MODEL,
        text,
        sources,
      };
      setMessages(prev => [...prev, modelMessage]);
    } catch (error) {
      const errorMessage: MessageType = {
        id: `error-${Date.now()}`,
        role: Role.ERROR,
        text: error instanceof Error ? error.message : "An unexpected error occurred.",
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  return (
    <div className="flex flex-col flex-grow h-full overflow-hidden">
      <div ref={messageListRef} className="flex-grow overflow-y-auto p-4 md:p-6 space-y-6">
        {messages.map((msg) => (
          <Message key={msg.id} message={msg} />
        ))}
        {isLoading && <Message key="loading" message={{ id: 'loading', role: Role.MODEL, text: '...' }} />}
      </div>
      <div className="p-4 md:p-6 border-t border-gray-200 dark:border-gray-700">
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};