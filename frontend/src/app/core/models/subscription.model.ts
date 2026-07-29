export type SubscriptionPlanCode = 'trial' | 'starter' | 'professional' | 'enterprise';

export interface PlanLimits {
  max_properties: number | null;
  max_units: number | null;
  max_team_members: number | null;
}

export interface Plan {
  code: SubscriptionPlanCode;
  name: string;
  price_monthly: string | null;
  currency: string;
  limits: PlanLimits;
  features: string[];
}

export interface UsageSummary {
  properties: number;
  units: number;
  team_members: number;
}

export interface CurrentSubscription {
  plan: Plan;
  usage: UsageSummary;
}

export interface SubscriptionEvent {
  id: string;
  previous_plan: SubscriptionPlanCode;
  new_plan: SubscriptionPlanCode;
  changed_by_name: string;
  reason: string;
  created_at: string;
}
