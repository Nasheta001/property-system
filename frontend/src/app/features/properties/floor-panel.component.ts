import { Component, OnInit, inject, input, output, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';

import { Floor, Unit } from '../../core/models/property.model';
import { PropertiesService } from '../../core/services/properties.service';
import { ConfirmDialogComponent } from '../../shared/ui/confirm-dialog/confirm-dialog.component';
import { FloorFormDialogComponent } from './floor-form-dialog.component';
import { UnitFormDialogComponent } from './unit-form-dialog.component';

@Component({
  selector: 'app-floor-panel',
  imports: [MatButtonModule, MatExpansionModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './floor-panel.component.html',
  styleUrl: './floor-panel.component.scss',
})
export class FloorPanelComponent implements OnInit {
  readonly floor = input.required<Floor>();
  readonly updated = output<Floor>();
  readonly deleted = output<string>();

  private readonly propertiesService = inject(PropertiesService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly units = signal<Unit[]>([]);
  protected readonly isLoaded = signal(false);
  protected readonly isLoading = signal(false);

  ngOnInit(): void {
    if (this.floor().unit_count === 0) {
      this.isLoaded.set(true);
    }
  }

  loadUnits(): void {
    if (this.isLoaded()) return;
    this.isLoading.set(true);
    this.propertiesService.listUnits({ floor: this.floor().id, page_size: 100 }).subscribe({
      next: (response) => {
        this.units.set(response.results);
        this.isLoaded.set(true);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  openCreateUnitDialog(): void {
    this.dialog
      .open(UnitFormDialogComponent, { data: { floorId: this.floor().id, unit: null } })
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.propertiesService.createUnit(payload).subscribe({
          next: (unit) => {
            this.units.update((list) => [...list, unit]);
            this.isLoaded.set(true);
            this.snackBar.open('Unit added.', 'Dismiss', { duration: 3000 });
          },
          error: (err) => this.showError(err),
        });
      });
  }

  openEditUnitDialog(unit: Unit): void {
    this.dialog
      .open(UnitFormDialogComponent, { data: { floorId: this.floor().id, unit } })
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.propertiesService.updateUnit(unit.id, payload).subscribe({
          next: (updated) => {
            this.units.update((list) => list.map((item) => (item.id === updated.id ? updated : item)));
            this.snackBar.open('Unit updated.', 'Dismiss', { duration: 3000 });
          },
          error: (err) => this.showError(err),
        });
      });
  }

  deleteUnit(unit: Unit): void {
    this.dialog
      .open(ConfirmDialogComponent, {
        data: { title: 'Delete unit', message: `Delete unit ${unit.unit_number}?`, confirmLabel: 'Delete', danger: true },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.propertiesService.deleteUnit(unit.id).subscribe({
          next: () => {
            this.units.update((list) => list.filter((item) => item.id !== unit.id));
            this.snackBar.open('Unit deleted.', 'Dismiss', { duration: 3000 });
          },
          error: (err) => this.showError(err),
        });
      });
  }

  editFloor(event: Event): void {
    event.stopPropagation();
    this.dialog
      .open(FloorFormDialogComponent, { data: { buildingId: this.floor().building, floor: this.floor() } })
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.propertiesService.updateFloor(this.floor().id, payload).subscribe({
          next: (updated) => {
            this.updated.emit(updated);
            this.snackBar.open('Floor updated.', 'Dismiss', { duration: 3000 });
          },
          error: (err) => this.showError(err),
        });
      });
  }

  deleteFloor(event: Event): void {
    event.stopPropagation();
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Delete floor',
          message: `Delete "${this.floor().name || 'Floor ' + this.floor().number}" and all its units?`,
          confirmLabel: 'Delete',
          danger: true,
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.propertiesService.deleteFloor(this.floor().id).subscribe({
          next: () => {
            this.deleted.emit(this.floor().id);
            this.snackBar.open('Floor deleted.', 'Dismiss', { duration: 3000 });
          },
          error: (err) => this.showError(err),
        });
      });
  }

  private showError(err: unknown): void {
    const message =
      (err as { error?: { error?: { message?: string } } })?.error?.error?.message ?? 'Something went wrong.';
    this.snackBar.open(message, 'Dismiss', { duration: 4000 });
  }
}
