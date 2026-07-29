export type LeaseStatus = 'draft' | 'active' | 'pending_renewal' | 'expired' | 'terminated';

export interface Lease {
  id: string;
  unit: string;
  unit_number: string;
  tenant: string;
  tenant_name: string;
  start_date: string;
  end_date: string | null;
  rent_amount: string;
  deposit_amount: string;
  billing_day: number;
  status: LeaseStatus;
  signed_at: string | null;
  terminated_at: string | null;
  termination_reason: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface LeaseCreatePayload {
  unit: string;
  tenant: string;
  start_date: string;
  end_date?: string | null;
  rent_amount: string;
  deposit_amount: string;
  billing_day: number;
  notes?: string;
}
