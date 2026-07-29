import { Component, OnInit, inject, input, output, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';

import { Building, Floor } from '../../core/models/property.model';
import { PropertiesService } from '../../core/services/properties.service';
import { ConfirmDialogComponent } from '../../shared/ui/confirm-dialog/confirm-dialog.component';
import { BuildingFormDialogComponent } from './building-form-dialog.component';
import { FloorFormDialogComponent } from './floor-form-dialog.component';
import { FloorPanelComponent } from './floor-panel.component';

@Component({
  selector: 'app-building-panel',
  imports: [MatButtonModule, MatExpansionModule, MatIconModule, MatProgressSpinnerModule, FloorPanelComponent],
  templateUrl: './building-panel.component.html',
  styleUrl: './building-panel.component.scss',
})
export class BuildingPanelComponent implements OnInit {
  readonly building = input.required<Building>();
  readonly updated = output<Building>();
  readonly deleted = output<string>();

  private readonly propertiesService = inject(PropertiesService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly floors = signal<Floor[]>([]);
  protected readonly isLoaded = signal(false);
  protected readonly isLoading = signal(false);

  ngOnInit(): void {
    if (this.building().floor_count === 0) {
      this.isLoaded.set(true);
    }
  }

  loadFloors(): void {
    if (this.isLoaded()) return;
    this.isLoading.set(true);
    this.propertiesService.listFloors({ building: this.building().id, page_size: 100 }).subscribe({
      next: (response) => {
        this.floors.set(response.results);
        this.isLoaded.set(true);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  openCreateFloorDialog(): void {
    this.dialog
      .open(FloorFormDialogComponent, { data: { buildingId: this.building().id, floor: null } })
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.propertiesService.createFloor(payload).subscribe({
          next: (floor) => {
            this.floors.update((list) => [...list, floor]);
            this.isLoaded.set(true);
            this.snackBar.open('Floor added.', 'Dismiss', { duration: 3000 });
          },
          error: (err) => this.showError(err),
        });
      });
  }

  onFloorUpdated(updated: Floor): void {
    this.floors.update((list) => list.map((item) => (item.id === updated.id ? updated : item)));
  }

  onFloorDeleted(id: string): void {
    this.floors.update((list) => list.filter((item) => item.id !== id));
  }

  editBuilding(event: Event): void {
    event.stopPropagation();
    this.dialog
      .open(BuildingFormDialogComponent, { data: { propertyId: this.building().property, building: this.building() } })
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.propertiesService.updateBuilding(this.building().id, payload).subscribe({
          next: (updated) => {
            this.updated.emit(updated);
            this.snackBar.open('Building updated.', 'Dismiss', { duration: 3000 });
          },
          error: (err) => this.showError(err),
        });
      });
  }

  deleteBuilding(event: Event): void {
    event.stopPropagation();
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Delete building',
          message: `Delete "${this.building().name}" and everything in it?`,
          confirmLabel: 'Delete',
          danger: true,
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.propertiesService.deleteBuilding(this.building().id).subscribe({
          next: () => {
            this.deleted.emit(this.building().id);
            this.snackBar.open('Building deleted.', 'Dismiss', { duration: 3000 });
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
