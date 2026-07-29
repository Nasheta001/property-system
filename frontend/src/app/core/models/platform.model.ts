import { SubscriptionPlanCode } from './subscription.model';

export interface PlatformOrganization {
  id: string;
  name: string;
  slug: string;
  subscription_plan: SubscriptionPlanCode;
  is_active: boolean;
  owner_email: string;
  member_count: number;
  property_count: number;
  unit_count: number;
  created_at: string;
}

export interface PlanBreakdownRow {
  plan: SubscriptionPlanCode;
  name: string;
  count: number;
}

export interface PlatformStats {
  total_organizations: number;
  active_organizations: number;
  suspended_organizations: number;
  total_users: number;
  total_properties: number;
  total_units: number;
  plan_breakdown: PlanBreakdownRow[];
  estimated_mrr: number;
}
