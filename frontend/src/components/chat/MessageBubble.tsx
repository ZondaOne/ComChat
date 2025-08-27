import React from 'react';
import { format } from 'date-fns';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  mediaUrl?: string;
  mediaType?: string;
}

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 group`}>
      <div className="flex items-end space-x-3 max-w-4xl">
        {!isUser && (
          <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-black flex items-center justify-center flex-shrink-0">
            <svg className="w-4 h-4 sm:w-5 sm:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
        )}
        
        <div className={`relative ${
          isUser 
            ? 'bg-black text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-xs sm:max-w-md ml-auto' 
            : 'bg-gray-100 text-gray-900 rounded-2xl rounded-tl-sm px-4 py-3 max-w-xs sm:max-w-md'
        }`}>
          
          
          {message.mediaUrl && message.mediaType?.startsWith('image/') && (
            <div className="mb-4 overflow-hidden rounded-2xl shadow-apple">
              <img 
                src={message.mediaUrl} 
                alt="Shared image"
                className="w-full max-w-sm object-cover transition-transform duration-300 group-hover:scale-105"
              />
            </div>
          )}
          
          <div className="whitespace-pre-wrap leading-relaxed text-sm sm:text-base">
            {message.content}
          </div>
          
          <div className={`flex items-center justify-end mt-3 text-xs ${
            isUser ? 'text-white/70' : 'text-gray-500'
          }`}>
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              {format(message.timestamp, 'HH:mm')}
            </span>
            {isUser && (
              <svg className="w-4 h-4 ml-2 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
        </div>
        
        {isUser && (
          <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0">
            <svg className="w-4 h-4 sm:w-5 sm:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;