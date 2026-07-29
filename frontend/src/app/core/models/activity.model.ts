export interface ActivityLogEntry {
  id: string;
  actor_name: string;
  verb: string;
  target_type: string;
  target_id: string;
  target_link: string;
  created_at: string;
}
