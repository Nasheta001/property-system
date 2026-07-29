export type DocumentType =
  | 'lease_agreement'
  | 'identification'
  | 'proof_of_payment'
  | 'inspection_report'
  | 'insurance'
  | 'contract'
  | 'other';

export interface PropertyDocument {
  id: string;
  title: string;
  description: string;
  document_type: DocumentType;
  file: string;
  property: string | null;
  property_name: string;
  lease: string | null;
  unit_number: string;
  tenant: string | null;
  tenant_name: string;
  uploaded_by_name: string;
  created_at: string;
  updated_at: string;
}
