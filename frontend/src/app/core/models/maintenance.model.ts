export interface Vendor {
  id: string;
  name: string;
  contact_person: string;
  phone_number: string;
  email: string;
  specialty: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type VendorPayload = Omit<Vendor, 'id' | 'created_at' | 'updated_at'>;

export type MaintenanceCategory =
  | 'plumbing'
  | 'electrical'
  | 'appliance'
  | 'structural'
  | 'hvac'
  | 'pest_control'
  | 'other';

export type MaintenancePriority = 'low' | 'medium' | 'high' | 'urgent';

export type MaintenanceStatus =
  | 'reported'
  | 'verified'
  | 'assigned'
  | 'accepted'
  | 'in_progress'
  | 'waiting_parts'
  | 'completed'
  | 'reviewed'
  | 'closed';

export interface MaintenanceRequest {
  id: string;
  unit: string;
  unit_number: string;
  tenant: string | null;
  tenant_name: string;
  reported_by_name: string;
  vendor_name: string;
  title: string;
  description: string;
  category: MaintenanceCategory;
  priority: MaintenancePriority;
  status: MaintenanceStatus;
  assigned_at: string | null;
  accepted_at: string | null;
  completed_at: string | null;
  reviewed_at: string | null;
  closed_at: string | null;
  closure_notes: string;
  comment_count: number;
  attachment_count: number;
  created_at: string;
  updated_at: string;
}

export interface MaintenanceRequestPayload {
  unit: string;
  tenant?: string | null;
  title: string;
  description?: string;
  category: MaintenanceCategory;
  priority: MaintenancePriority;
}

export interface MaintenanceComment {
  id: string;
  request: string;
  author_name: string;
  body: string;
  created_at: string;
}

export interface MaintenanceAttachment {
  id: string;
  request: string;
  file: string;
  caption: string;
  uploaded_by_name: string;
  created_at: string;
}
