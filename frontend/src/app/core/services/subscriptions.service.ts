import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../models/property.model';
import { CurrentSubscription, Plan, SubscriptionEvent } from '../models/subscription.model';

@Injectable({ providedIn: 'root' })
export class SubscriptionsService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/subscriptions`;

  listPlans(): Observable<Plan[]> {
    return this.http.get<Plan[]>(`${this.baseUrl}/plans/`);
  }

  getCurrent(): Observable<CurrentSubscription> {
    return this.http.get<CurrentSubscription>(`${this.baseUrl}/current/`);
  }

  changePlan(plan: SubscriptionPlanRequest): Observable<CurrentSubscription> {
    return this.http.post<CurrentSubscription>(`${this.baseUrl}/current/`, plan);
  }

  listEvents(): Observable<PaginatedResponse<SubscriptionEvent>> {
    return this.http.get<PaginatedResponse<SubscriptionEvent>>(`${this.baseUrl}/events/`);
  }
}

interface SubscriptionPlanRequest {
  plan: string;
  reason?: string;
}
