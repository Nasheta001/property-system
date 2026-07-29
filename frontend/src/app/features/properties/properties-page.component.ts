import { Component, OnInit, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';

import { Building, Property } from '../../core/models/property.model';
import { PropertiesService } from '../../core/services/properties.service';
import { ConfirmDialogComponent } from '../../shared/ui/confirm-dialog/confirm-dialog.component';
import { BuildingFormDialogComponent } from './building-form-dialog.component';
import { BuildingPanelComponent } from './building-panel.component';
import { PropertyFormDialogComponent } from './property-form-dialog.component';

interface PropertyRow {
  property: Property;
  buildings: Building[];
  isLoaded: boolean;
  isLoading: boolean;
}

@Component({
  selector: 'app-properties-page',
  imports: [
    MatButtonModule,
    MatExpansionModule,
    MatIconModule,
    MatProgressSpinnerModule,
    BuildingPanelComponent,
  ],
  templateUrl: './properties-page.component.html',
  styleUrl: './properties-page.component.scss',
})
export class PropertiesPageComponent implements OnInit {
  private readonly propertiesService = inject(PropertiesService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  protected readonly isLoading = signal(true);
  protected readonly rows = signal<PropertyRow[]>([]);

  ngOnInit(): void {
    this.load();
  }

  private load(): void {
    this.isLoading.set(true);
    this.propertiesService.list({ page_size: 100 }).subscribe({
      next: (response) => {
        this.rows.set(
          response.results.map((property) => ({
            property,
            buildings: [],
            isLoaded: property.building_count === 0,
            isLoading: false,
          }))
        );
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  loadBuildings(row: PropertyRow): void {
    if (row.isLoaded) return;
    this.patchRow(row.property.id, { isLoading: true });
    this.propertiesService.listBuildings({ property: row.property.id, page_size: 100 }).subscribe({
      next: (response) => this.patchRow(row.property.id, { buildings: response.results, isLoaded: true, isLoading: false }),
      error: () => this.patchRow(row.property.id, { isLoading: false }),
    });
  }

  private patchRow(propertyId: string, changes: Partial<PropertyRow>): void {
    this.rows.update((list) =>
      list.map((row) => (row.property.id === propertyId ? { ...row, ...changes } : row))
    );
  }

  openCreatePropertyDialog(): void {
    this.dialog
      .open(PropertyFormDialogComponent, { data: null })
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.propertiesService.createProperty(payload).subscribe({
          next: () => {
            this.snackBar.open('Property added.', 'Dismiss', { duration: 3000 });
            this.load();
          },
          error: (err) => this.showError(err),
        });
      });
  }

  openEditPropertyDialog(row: PropertyRow, event: Event): void {
    event.stopPropagation();
    this.dialog
      .open(PropertyFormDialogComponent, { data: row.property })
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.propertiesService.updateProperty(row.property.id, payload).subscribe({
          next: (updated) => {
            this.patchRow(row.property.id, { property: updated });
            this.snackBar.open('Property updated.', 'Dismiss', { duration: 3000 });
          },
          error: (err) => this.showError(err),
        });
      });
  }

  deleteProperty(row: PropertyRow, event: Event): void {
    event.stopPropagation();
    this.dialog
      .open(ConfirmDialogComponent, {
        data: {
          title: 'Delete property',
          message: `Delete "${row.property.name}" and everything in it?`,
          confirmLabel: 'Delete',
          danger: true,
        },
      })
      .afterClosed()
      .subscribe((confirmed) => {
        if (!confirmed) return;
        this.propertiesService.deleteProperty(row.property.id).subscribe({
          next: () => {
            this.rows.update((list) => list.filter((item) => item.property.id !== row.property.id));
            this.snackBar.open('Property deleted.', 'Dismiss', { duration: 3000 });
          },
          error: (err) => this.showError(err),
        });
      });
  }

  openCreateBuildingDialog(row: PropertyRow, event: Event): void {
    event.stopPropagation();
    this.dialog
      .open(BuildingFormDialogComponent, { data: { propertyId: row.property.id, building: null } })
      .afterClosed()
      .subscribe((payload) => {
        if (!payload) return;
        this.propertiesService.createBuilding(payload).subscribe({
          next: (building) => {
            this.patchRow(row.property.id, { buildings: [...row.buildings, building], isLoaded: true });
            this.snackBar.open('Building added.', 'Dismiss', { duration: 3000 });
          },
          error: (err) => this.showError(err),
        });
      });
  }

  onBuildingUpdated(row: PropertyRow, updated: Building): void {
    this.patchRow(row.property.id, {
      buildings: row.buildings.map((item) => (item.id === updated.id ? updated : item)),
    });
  }

  onBuildingDeleted(row: PropertyRow, id: string): void {
    this.patchRow(row.property.id, { buildings: row.buildings.filter((item) => item.id !== id) });
  }

  private showError(err: unknown): void {
    const message =
      (err as { error?: { error?: { message?: string } } })?.error?.error?.message ?? 'Something went wrong.';
    this.snackBar.open(message, 'Dismiss', { duration: 4000 });
  }
}
