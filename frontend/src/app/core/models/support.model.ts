export type TicketCategory = 'billing' | 'technical' | 'feature_request' | 'bug_report' | 'other';
export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent';
export type TicketStatus = 'open' | 'in_progress' | 'waiting_on_customer' | 'resolved' | 'closed';

export interface SupportTicket {
  id: string;
  subject: string;
  description: string;
  category: TicketCategory;
  priority: TicketPriority;
  status: TicketStatus;
  created_by_name: string;
  assigned_to_name: string;
  resolved_at: string | null;
  closed_at: string | null;
  comment_count: number;
  created_at: string;
  updated_at: string;
}

export interface SupportTicketPayload {
  subject: string;
  description: string;
  category: TicketCategory;
  priority: TicketPriority;
}

export interface SupportTicketComment {
  id: string;
  ticket: string;
  author_name: string;
  body: string;
  created_at: string;
}
