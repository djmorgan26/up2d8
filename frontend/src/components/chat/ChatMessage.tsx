import React from 'react';
import { ExternalLink } from 'lucide-react';
import { Badge } from '../ui/Badge';
import type { ChatMessage as ChatMessageType } from '../../types';

interface ChatMessageProps {
  message: ChatMessageType;
  onFollowUpClick?: (question: string) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onFollowUpClick,
}) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-3xl ${isUser ? 'ml-12' : 'mr-12'}`}>
        {/* Message bubble */}
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-primary text-white'
              : 'bg-white border border-border-light'
          }`}
        >
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        </div>

        {/* Citations */}
        {message.citations && message.citations.length > 0 && (
          <div className="mt-2 space-y-1">
            <p className="text-xs text-text-secondary font-medium">Sources:</p>
            {message.citations.map((citation, index) => (
              <a
                key={index}
                href={citation.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-primary hover:underline"
              >
                <ExternalLink className="h-3 w-3" />
                {citation.title}
              </a>
            ))}
          </div>
        )}

        {/* Follow-up questions */}
        {message.follow_up_questions && message.follow_up_questions.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.follow_up_questions.map((question, index) => (
              <button
                key={index}
                onClick={() => onFollowUpClick?.(question)}
                className="text-sm px-3 py-1.5 rounded-full bg-primary-pale text-primary hover:bg-primary-light transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <p className="text-xs text-text-tertiary mt-1">
          {new Date(message.created_at).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  );
};
