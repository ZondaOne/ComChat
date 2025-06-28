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
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
        isUser 
          ? 'bg-primary-600 text-white' 
          : 'bg-white text-gray-900 shadow-sm border'
      }`}>
        {message.mediaUrl && message.mediaType?.startsWith('image/') && (
          <img 
            src={message.mediaUrl} 
            alt="Shared image"
            className="w-full rounded mb-2 max-w-xs"
          />
        )}
        
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        
        <p className={`text-xs mt-1 ${
          isUser ? 'text-primary-100' : 'text-gray-500'
        }`}>
          {format(message.timestamp, 'HH:mm')}
        </p>
      </div>
    </div>
  );
};

export default MessageBubble;