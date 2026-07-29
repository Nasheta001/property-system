export type SearchResultType = 'property' | 'unit' | 'tenant' | 'payment' | 'maintenance' | 'document';

export interface SearchResult {
  type: SearchResultType;
  id: string;
  label: string;
  sublabel: string;
  link: string;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
}
