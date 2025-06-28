import React from 'react';

const Login: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">
            Sign in to ComChat
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Access your chatbot dashboard
          </p>
        </div>
        
        <div className="bg-white p-8 rounded-lg shadow">
          <p className="text-center text-gray-600">
            Authentication system coming soon...
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;