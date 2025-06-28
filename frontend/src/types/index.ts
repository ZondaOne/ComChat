export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  settings: Record<string, any>;
}

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: string;
  conversationId?: string;
}

export interface Conversation {
  id: string;
  messages: Message[];
  status: 'active' | 'closed';
  createdAt: string;
  updatedAt: string;
}

export interface Workflow {
  id: string;
  name: string;
  domain: string;
  description?: string;
  status: 'draft' | 'active' | 'paused' | 'archived';
  execution_count: number;
  success_rate: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}