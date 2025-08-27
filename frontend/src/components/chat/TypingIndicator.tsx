import React from 'react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start mb-6">
      <div className="flex items-end space-x-3 max-w-4xl">
        <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-black flex items-center justify-center flex-shrink-0">
          <svg className="w-4 h-4 sm:w-5 sm:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <div className="bg-gray-100 text-gray-900 rounded-2xl rounded-tl-sm px-4 py-3 max-w-xs sm:max-w-md">
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <span className="text-xs text-gray-500">Typing...</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;