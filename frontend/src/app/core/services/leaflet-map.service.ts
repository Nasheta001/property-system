import { Injectable } from '@angular/core';

export interface MapPin {
  id: string;
  lat: number;
  lng: number;
  title: string;
  subtitle: string;
}

export interface MapHandle {
  destroy: () => void;
}

/**
 * The one place that knows about the map rendering library. Built against
 * Leaflet + OpenStreetMap tiles — no API key, no billing account, unlike
 * Google Maps/Mapbox — so the map works out of the box in every
 * environment. Leaflet is imported dynamically so it never lands in the
 * main bundle for users who never open the Maps page, and tile-load
 * failures (e.g. no outbound network) are reported back through
 * `onTilesUnavailable` rather than left as a silently broken map, so the
 * caller can fall back to a plain list view.
 */
@Injectable({ providedIn: 'root' })
export class LeafletMapService {
  async render(
    container: HTMLElement,
    pins: MapPin[],
    options: { onPinClick?: (id: string) => void; onTilesUnavailable?: () => void }
  ): Promise<MapHandle> {
    const L = await import('leaflet');

    // Bundlers don't resolve Leaflet's default marker image URLs (they're
    // relative to leaflet.css, not to this module), so point them at the
    // copies served from /public/leaflet instead — otherwise every marker
    // renders as a broken image icon.
    L.Icon.Default.mergeOptions({
      iconUrl: 'leaflet/marker-icon.png',
      iconRetinaUrl: 'leaflet/marker-icon-2x.png',
      shadowUrl: 'leaflet/marker-shadow.png',
    });

    const center = pins.length > 0 ? [pins[0].lat, pins[0].lng] : [0, 0];
    const map = L.map(container).setView(center as [number, number], pins.length > 0 ? 12 : 2);

    const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    });

    let reportedUnavailable = false;
    tileLayer.on('tileerror', () => {
      if (reportedUnavailable) return;
      reportedUnavailable = true;
      options.onTilesUnavailable?.();
    });
    tileLayer.addTo(map);

    const markers = pins.map((pin) => {
      const marker = L.marker([pin.lat, pin.lng]).addTo(map);
      marker.bindPopup(`<strong>${escapeHtml(pin.title)}</strong><br>${escapeHtml(pin.subtitle)}`);
      marker.on('click', () => options.onPinClick?.(pin.id));
      return marker;
    });

    if (pins.length > 1) {
      const bounds = L.latLngBounds(pins.map((pin) => [pin.lat, pin.lng] as [number, number]));
      map.fitBounds(bounds, { padding: [32, 32] });
    }

    return {
      destroy: () => {
        markers.forEach((marker) => marker.remove());
        map.remove();
      },
    };
  }
}

function escapeHtml(value: string): string {
  const div = document.createElement('div');
  div.textContent = value;
  return div.innerHTML;
}
