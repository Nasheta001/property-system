export interface PaginatedResponse<T> {
  count: number;
  total_pages: number;
  current_page: number;
  page_size: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export type PropertyType = 'residential' | 'commercial' | 'mixed_use';

export interface Property {
  id: string;
  name: string;
  property_type: PropertyType;
  description: string;
  address: string;
  city: string;
  country: string;
  latitude: string | null;
  longitude: string | null;
  is_active: boolean;
  building_count: number;
  created_at: string;
  updated_at: string;
}

export type UnitStatus = 'vacant' | 'occupied' | 'under_maintenance' | 'reserved';

export interface Unit {
  id: string;
  floor: string;
  unit_number: string;
  unit_type: string;
  status: UnitStatus;
  bedrooms: number;
  bathrooms: number;
  size_sqm: string | null;
  rent_amount: string;
  deposit_amount: string;
  created_at: string;
  updated_at: string;
}
