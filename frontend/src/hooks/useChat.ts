import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../lib/api';
import type { ChatMessage } from '../types';

interface UseChatReturn {
  messages: ChatMessage[];
  isConnected: boolean;
  isLoading: boolean;
  sendMessage: (content: string) => void;
  disconnect: () => void;
}

export const useChat = (sessionId: string | null): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Load chat history
  useEffect(() => {
    if (!sessionId) return;

    const loadHistory = async () => {
      try {
        const history = await api.getChatHistory(sessionId);
        setMessages(history);
      } catch (error) {
        console.error('Failed to load chat history:', error);
      }
    };

    loadHistory();
  }, [sessionId]);

  // Connect to WebSocket
  useEffect(() => {
    if (!sessionId) return;

    const wsUrl = api.getWebSocketUrl(sessionId);
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'message_start') {
          // Add new assistant message placeholder
          setMessages((prev) => [
            ...prev,
            {
              id: data.message_id,
              role: 'assistant',
              content: '',
              created_at: new Date().toISOString(),
            },
          ]);
          setIsLoading(false);
        } else if (data.type === 'content_chunk') {
          // Append chunk to last message
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage && lastMessage.role === 'assistant') {
              lastMessage.content += data.chunk;
            }
            return newMessages;
          });
        } else if (data.type === 'message_complete') {
          // Update message with citations and follow-ups
          setMessages((prev) => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage && lastMessage.role === 'assistant') {
              lastMessage.citations = data.citations;
              lastMessage.follow_up_questions = data.follow_up_questions;
            }
            return newMessages;
          });
        } else if (data.type === 'error') {
          console.error('Chat error:', data.error);
          setIsLoading(false);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
      setIsLoading(false);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      setIsLoading(false);
    };

    return () => {
      ws.close();
    };
  }, [sessionId]);

  const sendMessage = useCallback(
    (content: string) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        console.error('WebSocket not connected');
        return;
      }

      // Add user message to UI immediately
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      // Send message through WebSocket
      wsRef.current.send(
        JSON.stringify({
          type: 'message',
          content,
        })
      );
    },
    []
  );

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  return {
    messages,
    isConnected,
    isLoading,
    sendMessage,
    disconnect,
  };
};
