export type PaymentMethod = 'mpesa' | 'card' | 'bank_transfer' | 'cash' | 'other';

export type PaymentStatus =
  | 'created'
  | 'pending'
  | 'processing'
  | 'paid'
  | 'settled'
  | 'refunded'
  | 'cancelled'
  | 'failed';

export interface Payment {
  id: string;
  lease: string;
  tenant_name: string;
  unit_number: string;
  amount: string;
  method: PaymentMethod;
  status: PaymentStatus;
  provider_reference: string;
  payment_date: string;
  receipt_number: string;
  receipt_sent_at: string | null;
  failure_reason: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface PaymentCreatePayload {
  lease: string;
  amount: string;
  method: PaymentMethod;
  payment_date: string;
  notes?: string;
}

export interface LedgerEntry {
  id: string;
  lease: string;
  unit_number: string;
  tenant_name: string;
  payment: string | null;
  entry_type: 'payment' | 'refund' | 'adjustment';
  amount: string;
  description: string;
  created_at: string;
}
