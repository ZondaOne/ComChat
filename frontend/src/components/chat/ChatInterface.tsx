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
    <div className="flex flex-col h-screen bg-surface-secondary">
      {/* Header */}
      <div className="bg-surface-elevated backdrop-blur-xl border-b border-gray-200/50 px-6 py-5 animate-slide-down">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-brand-500 to-brand-600 rounded-2xl flex items-center justify-center shadow-apple">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-4l-4 4z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-display font-bold text-gray-900">
                ComChat
              </h1>
              <p className="text-sm text-gray-600 font-medium">
                AI-powered support for {tenantSlug}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-3 py-2 bg-surface-primary rounded-xl shadow-apple">
              <div className="w-2 h-2 bg-accent-green rounded-full animate-pulse-subtle"></div>
              <span className="text-sm font-medium text-gray-700">Online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 && (
            <div className="text-center py-20 animate-fade-in-up">
              <div className="w-20 h-20 bg-gradient-to-br from-brand-500 to-brand-600 rounded-3xl mx-auto flex items-center justify-center mb-8 shadow-apple-lg">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 0 012 2v8a2 2 0 01-2 2h-4l-4 4z" />
                </svg>
              </div>
              <h3 className="text-2xl font-display font-bold text-gradient mb-4">
                Welcome to ComChat
              </h3>
              <p className="text-lg text-gray-600 max-w-lg mx-auto leading-relaxed">
                Start a conversation to get help from our AI assistant. You can ask questions, upload images, or get support for your needs.
              </p>
              <div className="mt-8 flex justify-center space-x-4">
                <div className="px-4 py-2 bg-surface-primary rounded-xl shadow-apple text-sm text-gray-600 border border-gray-200">
                  💬 Ask questions
                </div>
                <div className="px-4 py-2 bg-surface-primary rounded-xl shadow-apple text-sm text-gray-600 border border-gray-200">
                  📷 Upload images
                </div>
                <div className="px-4 py-2 bg-surface-primary rounded-xl shadow-apple text-sm text-gray-600 border border-gray-200">
                  🎯 Get support
                </div>
              </div>
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
      <div className="bg-surface-elevated backdrop-blur-xl border-t border-gray-200/50 px-4 py-6 animate-slide-up">
        <div className="max-w-4xl mx-auto">
          {selectedFile && (
            <div className="mb-4 p-4 bg-brand-50 rounded-2xl border border-brand-200 animate-scale-in">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-brand-500 rounded-xl flex items-center justify-center">
                    <PhotoIcon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <span className="text-sm font-medium text-brand-800">{selectedFile.name}</span>
                    <p className="text-xs text-brand-600">Image ready to send</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="w-8 h-8 flex items-center justify-center text-brand-600 hover:text-brand-800 hover:bg-brand-100 rounded-lg transition-all duration-200"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          )}
          
          <div className="flex items-end space-x-4">
            <div className="flex-1 relative">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Type your message..."
                rows={1}
                className="input-field text-base resize-none min-h-[3.5rem] max-h-32 py-4"
                disabled={isLoading}
              />
            </div>
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-12 h-12 flex items-center justify-center text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-xl transition-all duration-200 active:scale-95"
              disabled={isLoading}
            >
              <PhotoIcon className="h-6 w-6" />
            </button>
            
            <button
              onClick={handleSendMessage}
              disabled={isLoading || (!inputValue.trim() && !selectedFile)}
              className="w-12 h-12 bg-gradient-to-r from-brand-500 to-brand-600 text-white rounded-xl hover:shadow-apple-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 active:scale-95 flex items-center justify-center"
            >
              <PaperAirplaneIcon className="h-6 w-6" />
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