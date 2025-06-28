import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export interface ChatRequest {
  message: string;
  conversationId?: string;
  channel: string;
  channelUserId: string;  
  tenantSlug: string;
  mediaUrl?: string;
  mediaType?: string;
}

export interface ChatResponse {
  response: string;
  conversationId: string;
  messageId: string;
  processingTimeMs: number;
  aiModelUsed: string;
}

class ChatService {
  private apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
  });

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await this.apiClient.post<ChatResponse>('/chat/send', {
        message: request.message,
        conversation_id: request.conversationId,
        channel: request.channel,
        channel_user_id: request.channelUserId,
        tenant_slug: request.tenantSlug,
        media_url: request.mediaUrl,
        media_type: request.mediaType,
      });

      return {
        response: response.data.response,
        conversationId: response.data.conversationId,
        messageId: response.data.messageId,
        processingTimeMs: response.data.processingTimeMs,
        aiModelUsed: response.data.aiModelUsed,
      };
    } catch (error) {
      console.error('Chat service error:', error);
      throw new Error('Failed to send message');
    }
  }

  async getConversationMessages(conversationId: string) {
    try {
      const response = await this.apiClient.get(
        `/chat/conversations/${conversationId}/messages`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching conversation messages:', error);
      throw new Error('Failed to fetch messages');
    }
  }
}

export const chatService = new ChatService();