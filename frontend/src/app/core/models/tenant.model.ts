export interface TenantProfile {
  id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone_number: string;
  national_id: string;
  date_of_birth: string | null;
  employer: string;
  occupation: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  notes: string;
  active_lease_id: string | null;
  created_at: string;
  updated_at: string;
}

export type TenantProfilePayload = Omit<
  TenantProfile,
  'id' | 'full_name' | 'active_lease_id' | 'created_at' | 'updated_at'
>;
