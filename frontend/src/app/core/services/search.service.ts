import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { SearchResponse } from '../models/search.model';

@Injectable({ providedIn: 'root' })
export class SearchService {
  private readonly http = inject(HttpClient);

  search(query: string): Observable<SearchResponse> {
    return this.http.get<SearchResponse>(`${environment.apiUrl}/search/`, {
      params: new HttpParams({ fromObject: { q: query } }),
    });
  }
}
