import { create } from 'zustand';
import { ChatMessage } from '../types';
import { sendChatMessage } from '../services/chatService';
import { saveChatHistory, getChatHistory, clearChatHistory } from '../services/storageService';

interface ChatState {
  // State
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;

  // Actions
  sendMessage: (prompt: string) => Promise<void>;
  loadChatHistory: () => Promise<void>;
  clearChat: () => Promise<void>;
  setError: (error: string | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  // Initial state
  messages: [],
  isLoading: false,
  error: null,

  // Send a message to the AI
  sendMessage: async (prompt: string) => {
    if (!prompt || prompt.trim().length === 0) {
      set({ error: 'Message cannot be empty' });
      return;
    }

    const { messages } = get();

    // Add user message to chat
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: prompt.trim(),
      timestamp: new Date(),
    };

    const updatedMessages = [...messages, userMessage];
    set({ messages: updatedMessages, isLoading: true, error: null });

    // Save to storage
    await saveChatHistory(updatedMessages);

    try {
      // Call API
      const response = await sendChatMessage(prompt);

      // Add AI response to chat
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.text,
        sources: response.sources,
        timestamp: new Date(),
      };

      const finalMessages = [...updatedMessages, aiMessage];
      set({
        messages: finalMessages,
        isLoading: false,
      });

      // Save to storage
      await saveChatHistory(finalMessages);

    } catch (error: any) {
      console.error('[ChatStore] Error sending message:', error);
      set({
        isLoading: false,
        error: error.message || 'Failed to send message',
      });

      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };

      const messagesWithError = [...updatedMessages, errorMessage];
      set({ messages: messagesWithError });

      // Save to storage
      await saveChatHistory(messagesWithError);
    }
  },

  // Load chat history from storage
  loadChatHistory: async () => {
    try {
      const history = await getChatHistory();
      set({ messages: history });
      console.log(`[ChatStore] Loaded ${history.length} messages from history`);
    } catch (error) {
      console.error('[ChatStore] Error loading chat history:', error);
    }
  },

  // Clear all chat messages
  clearChat: async () => {
    set({ messages: [], error: null });
    await clearChatHistory();
    console.log('[ChatStore] Chat cleared');
  },

  // Set error manually
  setError: (error: string | null) => {
    set({ error });
  },
}));
