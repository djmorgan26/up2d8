import React from 'react';
import { useParams } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { ChatInterface } from '../components/chat/ChatInterface';

export const ChatPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();

  if (!sessionId) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <p className="text-text-secondary">Invalid chat session</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      <Header />
      <div className="flex-1 overflow-hidden">
        <ChatInterface
          sessionId={sessionId}
          suggestedQuestions={[
            "What are the key trends in this digest?",
            "Summarize the most important developments",
            "Which companies are mentioned most frequently?",
            "What should I focus on today?",
          ]}
        />
      </div>
    </div>
  );
};
