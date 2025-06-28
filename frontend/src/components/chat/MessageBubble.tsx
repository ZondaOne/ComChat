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
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-brand-500 to-brand-600 flex items-center justify-center shadow-apple group-hover:scale-110 transition-transform duration-300 flex-shrink-0">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-4l-4 4z" />
            </svg>
          </div>
        )}
        
        <div className={`relative ${
          isUser 
            ? 'message-bubble-user ml-auto' 
            : 'message-bubble-bot'
        }`}>
          {/* Shimmer effect for user messages */}
          {isUser && (
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transform translate-x-[-200%] group-hover:translate-x-[200%] skew-x-12 transition-all duration-1000 rounded-3xl"></div>
          )}
          
          {!isUser && (
            <div className="flex items-center mb-3">
              <span className="text-xs font-medium text-brand-600 tracking-wide">ComChat Assistant</span>
            </div>
          )}
          
          {message.mediaUrl && message.mediaType?.startsWith('image/') && (
            <div className="mb-4 overflow-hidden rounded-2xl shadow-apple">
              <img 
                src={message.mediaUrl} 
                alt="Shared image"
                className="w-full max-w-sm object-cover transition-transform duration-300 group-hover:scale-105"
              />
            </div>
          )}
          
          <div className="whitespace-pre-wrap leading-relaxed text-base">
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
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center shadow-apple group-hover:scale-110 transition-transform duration-300 flex-shrink-0">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;