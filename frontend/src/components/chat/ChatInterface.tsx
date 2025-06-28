import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { PaperAirplaneIcon, PhotoIcon } from '@heroicons/react/24/solid';
import toast from 'react-hot-toast';

import { chatService } from '../../services/chatService';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  mediaUrl?: string;
  mediaType?: string;
}

const ChatInterface: React.FC = () => {
  const { tenantSlug = 'demo' } = useParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() && !selectedFile) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
      mediaUrl: selectedFile ? URL.createObjectURL(selectedFile) : undefined,
      mediaType: selectedFile?.type
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage({
        message: inputValue,
        conversationId: conversationId ?? undefined,
        channel: 'web',
        channelUserId: 'web-user-' + Date.now(),
        tenantSlug,
        mediaUrl: selectedFile ? await uploadFile(selectedFile) : undefined,
        mediaType: selectedFile?.type
      });

      const botMessage: Message = {
        id: response.messageId,
        content: response.response,
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
      
      if (!conversationId) {
        setConversationId(response.conversationId);
      }
      
      setSelectedFile(null);
      
    } catch (error) {
      toast.error('Failed to send message. Please try again.');
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const uploadFile = async (file: File): Promise<string> => {
    // TODO: Implement file upload
    return URL.createObjectURL(file);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type.startsWith('image/')) {
        setSelectedFile(file);
      } else {
        toast.error('Only image files are supported');
      }
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b px-6 py-4">
        <h1 className="text-xl font-semibold text-gray-900">
          ComChat - {tenantSlug}
        </h1>
        <p className="text-sm text-gray-500">
          AI-powered customer support
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-500 mb-2">👋</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Welcome to ComChat!
              </h3>
              <p className="text-gray-600">
                Send a message to get started. You can also share images for analysis.
              </p>
            </div>
          )}
          
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {isLoading && <TypingIndicator />}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t px-4 py-4">
        <div className="max-w-4xl mx-auto">
          {selectedFile && (
            <div className="mb-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <PhotoIcon className="h-5 w-5 text-blue-600" />
                  <span className="text-sm text-blue-800">{selectedFile.name}</span>
                </div>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </div>
            </div>
          )}
          
          <div className="flex items-end space-x-3">
            <div className="flex-1 relative">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                rows={1}
                className="w-full resize-none border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                disabled={isLoading}
              />
            </div>
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-3 text-gray-400 hover:text-gray-600 transition-colors"
              disabled={isLoading}
            >
              <PhotoIcon className="h-5 w-5" />
            </button>
            
            <button
              onClick={handleSendMessage}
              disabled={isLoading || (!inputValue.trim() && !selectedFile)}
              className="bg-primary-600 text-white p-3 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </div>
          
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;