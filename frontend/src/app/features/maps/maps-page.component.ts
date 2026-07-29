import { Component, ElementRef, Injector, OnDestroy, OnInit, ViewChild, afterNextRender, inject, signal } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { Property } from '../../core/models/property.model';
import { PropertiesService } from '../../core/services/properties.service';
import { LeafletMapService, MapHandle, MapPin } from '../../core/services/leaflet-map.service';

@Component({
  selector: 'app-maps-page',
  imports: [MatIconModule, MatProgressSpinnerModule],
  templateUrl: './maps-page.component.html',
  styleUrl: './maps-page.component.scss',
})
export class MapsPageComponent implements OnInit, OnDestroy {
  private readonly propertiesService = inject(PropertiesService);
  private readonly leafletMapService = inject(LeafletMapService);
  private readonly injector = inject(Injector);

  @ViewChild('mapContainer') private mapContainer?: ElementRef<HTMLDivElement>;

  protected readonly isLoading = signal(true);
  protected readonly properties = signal<Property[]>([]);
  protected readonly tilesUnavailable = signal(false);
  protected readonly highlightedId = signal<string | null>(null);

  private mapHandle: MapHandle | null = null;

  ngOnInit(): void {
    this.propertiesService.list({ page_size: 200 }).subscribe({
      next: (response) => {
        this.properties.set(response.results);
        this.isLoading.set(false);
        // `#mapContainer` only exists in the DOM once the `@if` in the
        // template re-renders for the new signal values — afterNextRender
        // waits for exactly that, so `this.mapContainer` is guaranteed set.
        afterNextRender(() => this.tryRenderMap(), { injector: this.injector });
      },
      error: () => this.isLoading.set(false),
    });
  }

  ngOnDestroy(): void {
    this.mapHandle?.destroy();
  }

  protected get pinnedProperties(): Property[] {
    return this.properties().filter((property) => property.latitude !== null && property.longitude !== null);
  }

  focusProperty(property: Property): void {
    this.highlightedId.set(property.id);
  }

  protected propertyAddress(property: Property): string {
    return [property.address, property.city, property.country].filter(Boolean).join(', ') || 'No address on file';
  }

  private tryRenderMap(): void {
    if (!this.mapContainer) return;

    const pins: MapPin[] = this.pinnedProperties.map((property) => ({
      id: property.id,
      lat: Number(property.latitude),
      lng: Number(property.longitude),
      title: property.name,
      subtitle: [property.address, property.city].filter(Boolean).join(', '),
    }));

    if (pins.length === 0) return;

    this.leafletMapService
      .render(this.mapContainer.nativeElement, pins, {
        onPinClick: (id) => this.highlightedId.set(id),
        onTilesUnavailable: () => this.tilesUnavailable.set(true),
      })
      .then((handle) => {
        this.mapHandle = handle;
      });
  }
}
