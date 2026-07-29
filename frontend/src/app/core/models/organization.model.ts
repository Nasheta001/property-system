export type MembershipRole =
  | 'owner'
  | 'admin'
  | 'property_manager'
  | 'landlord'
  | 'accountant'
  | 'auditor'
  | 'vendor'
  | 'tenant';

export interface OrganizationMembershipSummary {
  organization_id: string;
  organization_name: string;
  organization_slug: string;
  role: MembershipRole;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  subscription_plan: 'trial' | 'starter' | 'professional' | 'enterprise';
  is_active: boolean;
  email: string;
  phone_number: string;
  address: string;
  city: string;
  country: string;
  timezone: string;
  currency: string;
  role: MembershipRole | null;
  created_at: string;
}
