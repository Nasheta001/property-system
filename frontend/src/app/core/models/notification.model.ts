export type NotificationType =
  | 'lease_activated'
  | 'lease_terminated'
  | 'payment_received'
  | 'payment_refunded'
  | 'maintenance_reported'
  | 'maintenance_status_changed'
  | 'generic';

export interface AppNotification {
  id: string;
  notification_type: NotificationType;
  title: string;
  body: string;
  link: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}
