import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { OrganizationMembershipSummary } from '../models/organization.model';
import { User } from '../models/user.model';
import { TokenStorageService } from './token-storage.service';

interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
  memberships: OrganizationMembershipSummary[];
}

interface RegisterResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly tokenStorage = inject(TokenStorageService);

  private readonly baseUrl = `${environment.apiUrl}/auth`;

  readonly currentUser = signal<User | null>(null);
  readonly memberships = signal<OrganizationMembershipSummary[]>([]);
  readonly isAuthenticated = computed(() => this.currentUser() !== null);
  readonly isBootstrapping = signal(true);

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.baseUrl}/login/`, { email, password }).pipe(
      tap((response) => {
        this.tokenStorage.setTokens(response.access, response.refresh);
        this.currentUser.set(response.user);
        this.memberships.set(response.memberships);
      })
    );
  }

  register(payload: RegisterPayload): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${this.baseUrl}/register/`, payload).pipe(
      tap((response) => {
        this.tokenStorage.setTokens(response.access, response.refresh);
        this.currentUser.set(response.user);
      })
    );
  }

  logout(): Observable<void> {
    const refresh = this.tokenStorage.getRefreshToken();
    return new Observable<void>((subscriber) => {
      const finish = () => {
        this.tokenStorage.clear();
        this.currentUser.set(null);
        this.memberships.set([]);
        subscriber.next();
        subscriber.complete();
      };
      if (!refresh) {
        finish();
        return;
      }
      this.http.post(`${this.baseUrl}/logout/`, { refresh }).subscribe({ next: finish, error: finish });
    });
  }

  /** Rehydrates the session from a stored token on app boot / page reload. */
  bootstrap(): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/me/`).pipe(tap((user) => this.currentUser.set(user)));
  }

  hasStoredSession(): boolean {
    return this.tokenStorage.getAccessToken() !== null;
  }
}
