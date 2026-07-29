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

export type PropertyPayload = Pick<
  Property,
  'name' | 'property_type' | 'description' | 'address' | 'city' | 'country' | 'is_active' | 'latitude' | 'longitude'
>;

export interface Building {
  id: string;
  property: string;
  name: string;
  code: string;
  floor_count: number;
  created_at: string;
  updated_at: string;
}

export type BuildingPayload = Pick<Building, 'property' | 'name' | 'code'>;

export interface Floor {
  id: string;
  building: string;
  number: number;
  name: string;
  unit_count: number;
  created_at: string;
  updated_at: string;
}

export type FloorPayload = Pick<Floor, 'building' | 'number' | 'name'>;

export type UnitStatus = 'vacant' | 'occupied' | 'under_maintenance' | 'reserved';

export type UnitType =
  | 'studio'
  | 'one_bedroom'
  | 'two_bedroom'
  | 'three_bedroom'
  | 'penthouse'
  | 'office'
  | 'shop'
  | 'other';

export interface Unit {
  id: string;
  floor: string;
  unit_number: string;
  unit_type: UnitType;
  status: UnitStatus;
  bedrooms: number;
  bathrooms: number;
  size_sqm: string | null;
  rent_amount: string;
  deposit_amount: string;
  created_at: string;
  updated_at: string;
}

export type UnitPayload = Pick<
  Unit,
  'floor' | 'unit_number' | 'unit_type' | 'bedrooms' | 'bathrooms' | 'size_sqm' | 'rent_amount' | 'deposit_amount'
>;
