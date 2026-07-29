import { Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { MatBadgeModule } from '@angular/material/badge';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router } from '@angular/router';
import { Subscription, interval, startWith, switchMap } from 'rxjs';

import { AppNotification } from '../../../core/models/notification.model';
import { NotificationsService } from '../../../core/services/notifications.service';

const POLL_INTERVAL_MS = 60000;

@Component({
  selector: 'app-notification-bell',
  imports: [MatBadgeModule, MatButtonModule, MatIconModule, MatMenuModule, MatProgressSpinnerModule],
  templateUrl: './notification-bell.component.html',
  styleUrl: './notification-bell.component.scss',
})
export class NotificationBellComponent implements OnInit, OnDestroy {
  private readonly notificationsService = inject(NotificationsService);
  private readonly router = inject(Router);
  private pollSubscription?: Subscription;

  protected readonly unreadCount = signal(0);
  protected readonly notifications = signal<AppNotification[]>([]);
  protected readonly isLoading = signal(false);

  ngOnInit(): void {
    this.pollSubscription = interval(POLL_INTERVAL_MS)
      .pipe(
        startWith(0),
        switchMap(() => this.notificationsService.unreadCount())
      )
      .subscribe({ next: (response) => this.unreadCount.set(response.count) });
  }

  ngOnDestroy(): void {
    this.pollSubscription?.unsubscribe();
  }

  onMenuOpened(): void {
    this.isLoading.set(true);
    this.notificationsService.list({ page_size: 10 }).subscribe({
      next: (response) => {
        this.notifications.set(response.results);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  openNotification(notification: AppNotification): void {
    if (!notification.is_read) {
      this.notificationsService.markRead(notification.id).subscribe(() => {
        this.unreadCount.update((count) => Math.max(0, count - 1));
      });
    }
    if (notification.link) {
      this.router.navigateByUrl(notification.link);
    }
  }

  markAllRead(event: Event): void {
    event.stopPropagation();
    this.notificationsService.markAllRead().subscribe(() => {
      this.unreadCount.set(0);
      this.notifications.update((list) => list.map((item) => ({ ...item, is_read: true })));
    });
  }
}
