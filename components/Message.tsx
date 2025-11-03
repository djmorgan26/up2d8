
import React from 'react';
import { Message as MessageType, Role } from '../types';
import { Sources } from './Sources';

interface MessageProps {
  message: MessageType;
}

const UserIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
);

const BotIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor"><path d="M19.98 10.32c.01.16.02.32.02.48s-.01.32-.02.48l1.63 1.28c.13.1.18.28.1.43l-1.6 2.77c-.08.15-.27.21-.42.14l-1.95-.8a5.94 5.94 0 0 1-2.43 1.34l-.29 2.08c-.03.17-.18.3-.35.3h-3.2c-.17 0-.32-.13-.35-.3l-.29-2.08a5.94 5.94 0 0 1-2.43-1.34l-1.95.8c-.15.07-.34.01-.42-.14l-1.6-2.77c-.08-.15-.03-.33.1-.43l1.63-1.28c-.01-.16-.02-.32-.02-.48s.01-.32.02-.48L2.5 9.04c-.13-.1-.18-.28-.1-.43l1.6-2.77c.08-.15.27-.21.42-.14l1.95.8a5.94 5.94 0 0 1 2.43-1.34l.29-2.08c.03-.17.18-.3.35-.3h3.2c.17 0 .32.13.35.3l.29 2.08a5.94 5.94 0 0 1 2.43 1.34l1.95-.8c.15-.07.34-.01.42.14l1.6 2.77c.08.15.03.33-.1.43l-1.63 1.28zM12 15c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z"/></svg>
);

const ErrorIcon = () => (
   <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
);


export const Message: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.role === Role.USER;
  const isError = message.role === Role.ERROR;

  const wrapperClasses = `flex items-start gap-3 max-w-xl ${isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'}`;
  
  const iconWrapperClasses = `flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white ${
    isUser ? 'bg-blue-500' : isError ? 'bg-red-500' : 'bg-gray-500'
  }`;

  const bubbleClasses = `p-3 px-4 rounded-2xl text-base ${
    isUser
      ? 'bg-blue-100 dark:bg-blue-800 text-gray-900 dark:text-white rounded-br-none'
      : isError
      ? 'bg-red-100 dark:bg-red-900/50 border border-red-300 dark:border-red-500 text-red-900 dark:text-red-100 rounded-bl-none'
      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-none'
  }`;
  
  const formattedText = message.text.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>').replace(/\n/g, '<br />');

  return (
    <div className={wrapperClasses}>
      <div className={iconWrapperClasses}>
        {isUser ? <UserIcon /> : isError ? <ErrorIcon /> : <BotIcon />}
      </div>
      <div className="flex flex-col">
        <div className={bubbleClasses}>
            {message.text === '...' ? (
                <div className="flex items-center justify-center space-x-1.5">
                    <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-pulse [animation-delay:-0.3s]"></div>
	                <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-pulse [animation-delay:-0.15s]"></div>
	                <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-pulse"></div>
                </div>
            ) : (
              <div className="whitespace-pre-wrap selection:bg-blue-200 dark:selection:bg-blue-500" dangerouslySetInnerHTML={{ __html: formattedText }}></div>
            )}
        </div>
        {message.sources && message.sources.length > 0 && <Sources sources={message.sources} />}
      </div>
    </div>
  );
};