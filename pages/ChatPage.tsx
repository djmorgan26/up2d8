
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Message as MessageType, Role } from '../types';
import { askGeminiWithSearch } from '../services/geminiService';
import { Message } from '../components/Message';
import { ChatInput } from '../components/ChatInput';

const ChatPage: React.FC = () => {
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
      id: Date.now().toString(),
      role: Role.USER,
      content: prompt,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const { text, sources } = await askGeminiWithSearch(prompt);
const modelMessage: MessageType = {
        id: Date.now().toString(),
        role: Role.MODEL,
        content: geminiResponse.text, // The backend still returns 'text'
        timestamp: new Date().toISOString(),
        sources: geminiResponse.sources,
      };
      setMessages(prev => [...prev, modelMessage]);
    } catch (error) {
const errorMessage: MessageType = {
      id: Date.now().toString(),
      role: Role.ERROR,
      content: error instanceof Error ? error.message : "An unexpected error occurred.",
    };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  return (
    <div className="flex flex-col h-full">
      <div ref={messageListRef} className="flex-grow overflow-y-auto p-4 md:p-6 space-y-6">
        {messages.map((msg) => (
          <Message key={msg.id} message={msg} />
        ))}
        {isLoading && <Message key="loading" message={{ id: 'loading', role: Role.MODEL, content: '...' }} />}
      </div>
      <div className="p-4 md:p-6 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex-shrink-0">
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default ChatPage;
