export type CalendarEventType =
  | 'lease_start'
  | 'lease_end'
  | 'rent_due'
  | 'payment_received'
  | 'maintenance_reported'
  | 'maintenance_completed';

export type CalendarObjectType = 'lease' | 'payment' | 'maintenance';

export interface CalendarEvent {
  id: string;
  date: string;
  type: CalendarEventType;
  title: string;
  subtitle: string;
  object_type: CalendarObjectType;
  object_id: string;
}

export interface CalendarEventsResponse {
  start: string;
  end: string;
  events: CalendarEvent[];
}
