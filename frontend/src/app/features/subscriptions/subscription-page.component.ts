import { DatePipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { forkJoin } from 'rxjs';

import { OrganizationService } from '../../core/services/organization.service';
import { SubscriptionsService } from '../../core/services/subscriptions.service';
import { CurrentSubscription, Plan, SubscriptionEvent } from '../../core/models/subscription.model';
import { ConfirmDialogComponent } from '../../shared/ui/confirm-dialog/confirm-dialog.component';

const ADMIN_ROLES = new Set(['owner', 'admin']);
const PLAN_ORDER = ['trial', 'starter', 'professional', 'enterprise'];

interface UsageRow {
  label: string;
  used: number;
  limit: number | null;
  percent: number;
  overLimit: boolean;
}

@Component({
  selector: 'app-subscription-page',
  imports: [DatePipe, MatButtonModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './subscription-page.component.html',
  styleUrl: './subscription-page.component.scss',
})
export class SubscriptionPageComponent implements OnInit {
  private readonly subscriptionsService = inject(SubscriptionsService);
  private readonly organizationService = inject(OrganizationService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly isLoading = signal(true);
  protected readonly current = signal<CurrentSubscription | null>(null);
  protected readonly plans = signal<Plan[]>([]);
  protected readonly events = signal<SubscriptionEvent[]>([]);

  protected readonly canManage = computed(() => {
    const role = this.organizationService.activeOrganization()?.role;
    return !!role && ADMIN_ROLES.has(role);
  });

  protected readonly usageRows = computed<UsageRow[]>(() => {
    const subscription = this.current();
    if (!subscription) return [];
    const { usage, plan } = subscription;
    return [
      { key: 'properties' as const, label: 'Properties' },
      { key: 'units' as const, label: 'Units' },
      { key: 'team_members' as const, label: 'Team members' },
    ].map(({ key, label }) => {
      const limitKey = `max_${key}` as keyof Plan['limits'];
      const limit = plan.limits[limitKey];
      const used = usage[key];
      return {
        label,
        used,
        limit,
        percent: limit ? Math.min(100, Math.round((used / limit) * 100)) : 0,
        overLimit: limit !== null && used > limit,
      };
    });
  });

  ngOnInit(): void {
    this.load();
  }

  private load(): void {
    this.isLoading.set(true);
    forkJoin({
      current: this.subscriptionsService.getCurrent(),
      plans: this.subscriptionsService.listPlans(),
      events: this.subscriptionsService.listEvents(),
    }).subscribe({
      next: ({ current, plans, events }) => {
        this.current.set(current);
        this.plans.set(this.sortedPlans(plans));
        this.events.set(events.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  private sortedPlans(plans: Plan[]): Plan[] {
    return [...plans].sort((a, b) => PLAN_ORDER.indexOf(a.code) - PLAN_ORDER.indexOf(b.code));
  }

  switchPlan(plan: Plan): void {
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Switch subscription plan',
          message: `Switch this organization to the ${plan.name} plan?`,
          confirmLabel: 'Switch plan',
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.subscriptionsService.changePlan({ plan: plan.code }).subscribe({
          next: () => {
            this.snackBar.open(`Switched to the ${plan.name} plan.`, 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  formatLimit(limit: number | null): string {
    return limit === null ? 'Unlimited' : String(limit);
  }

  formatPrice(plan: Plan): string {
    if (plan.price_monthly === null) return 'Contact us';
    return Number(plan.price_monthly) === 0 ? 'Free' : `$${Number(plan.price_monthly).toFixed(0)}/mo`;
  }

  private showError(err: unknown): void {
    const message =
      (err as { error?: { error?: { message?: string } } })?.error?.error?.message ?? 'Something went wrong.';
    this.snackBar.open(message, 'Dismiss', { duration: 5000 });
  }
}
