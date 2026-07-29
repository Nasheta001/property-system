export type AIMessageRole = 'user' | 'assistant';

export interface AIMessage {
  id: string;
  role: AIMessageRole;
  content: string;
  provider: string;
  created_at: string;
}

export interface AIConversation {
  id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface StartConversationResponse {
  conversation: AIConversation;
  message: AIMessage;
}
