import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router } from '@angular/router';

import { CalendarEvent, CalendarEventType } from '../../core/models/calendar.model';
import { CalendarService } from '../../core/services/calendar.service';

interface GridCell {
  dateKey: string;
  dayNumber: number;
  inCurrentMonth: boolean;
  isToday: boolean;
  events: CalendarEvent[];
}

interface LegendItem {
  type: CalendarEventType;
  label: string;
}

const WEEKDAY_LABELS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const OBJECT_ROUTES: Record<CalendarEvent['object_type'], string> = {
  lease: '/leases',
  payment: '/payments',
  maintenance: '/maintenance',
};

function dateKey(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

function isSameDay(a: Date, b: Date): boolean {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
}

@Component({
  selector: 'app-calendar-page',
  imports: [MatButtonModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './calendar-page.component.html',
  styleUrl: './calendar-page.component.scss',
})
export class CalendarPageComponent implements OnInit {
  private readonly calendarService = inject(CalendarService);
  private readonly router = inject(Router);

  protected readonly weekdayLabels = WEEKDAY_LABELS;
  protected readonly legend: LegendItem[] = [
    { type: 'lease_start', label: 'Lease starts' },
    { type: 'lease_end', label: 'Lease ends' },
    { type: 'rent_due', label: 'Rent due' },
    { type: 'payment_received', label: 'Payment received' },
    { type: 'maintenance_reported', label: 'Maintenance reported' },
    { type: 'maintenance_completed', label: 'Maintenance completed' },
  ];

  protected readonly isLoading = signal(true);
  protected readonly viewedMonth = signal(this.startOfMonth(new Date()));
  protected readonly eventsByDate = signal<Map<string, CalendarEvent[]>>(new Map());

  protected readonly monthLabel = computed(() =>
    this.viewedMonth().toLocaleDateString(undefined, { month: 'long', year: 'numeric' })
  );

  protected readonly gridCells = computed<GridCell[]>(() => {
    const month = this.viewedMonth();
    const gridStart = this.startOfGrid(month);
    const today = new Date();
    const events = this.eventsByDate();

    return Array.from({ length: 42 }, (_, index) => {
      const cellDate = addDays(gridStart, index);
      const key = dateKey(cellDate);
      return {
        dateKey: key,
        dayNumber: cellDate.getDate(),
        inCurrentMonth: cellDate.getMonth() === month.getMonth(),
        isToday: isSameDay(cellDate, today),
        events: events.get(key) ?? [],
      };
    });
  });

  ngOnInit(): void {
    this.load();
  }

  previousMonth(): void {
    const month = this.viewedMonth();
    this.viewedMonth.set(new Date(month.getFullYear(), month.getMonth() - 1, 1));
    this.load();
  }

  nextMonth(): void {
    const month = this.viewedMonth();
    this.viewedMonth.set(new Date(month.getFullYear(), month.getMonth() + 1, 1));
    this.load();
  }

  goToToday(): void {
    this.viewedMonth.set(this.startOfMonth(new Date()));
    this.load();
  }

  openEvent(event: CalendarEvent): void {
    this.router.navigate([OBJECT_ROUTES[event.object_type]]);
  }

  private load(): void {
    this.isLoading.set(true);
    const gridStart = this.startOfGrid(this.viewedMonth());
    const gridEnd = addDays(gridStart, 41);

    this.calendarService.getEvents(dateKey(gridStart), dateKey(gridEnd)).subscribe({
      next: (response) => {
        const grouped = new Map<string, CalendarEvent[]>();
        for (const event of response.events) {
          const list = grouped.get(event.date) ?? [];
          list.push(event);
          grouped.set(event.date, list);
        }
        this.eventsByDate.set(grouped);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  private startOfMonth(date: Date): Date {
    return new Date(date.getFullYear(), date.getMonth(), 1);
  }

  private startOfGrid(month: Date): Date {
    return addDays(month, -month.getDay());
  }
}
