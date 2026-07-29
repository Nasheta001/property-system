import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatAutocompleteModule, MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { Router } from '@angular/router';
import { debounceTime, distinctUntilChanged, of, switchMap } from 'rxjs';

import { SearchResult, SearchResultType } from '../../../core/models/search.model';
import { SearchService } from '../../../core/services/search.service';

const MIN_QUERY_LENGTH = 2;

@Component({
  selector: 'app-global-search',
  imports: [ReactiveFormsModule, MatAutocompleteModule, MatFormFieldModule, MatIconModule, MatInputModule],
  templateUrl: './global-search.component.html',
  styleUrl: './global-search.component.scss',
})
export class GlobalSearchComponent {
  private readonly searchService = inject(SearchService);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly control = new FormControl('', { nonNullable: true });
  protected readonly results = signal<SearchResult[]>([]);
  protected readonly isSearching = signal(false);

  constructor() {
    this.control.valueChanges
      .pipe(
        debounceTime(250),
        distinctUntilChanged(),
        switchMap((query) => {
          if (query.trim().length < MIN_QUERY_LENGTH) {
            this.results.set([]);
            return of(null);
          }
          this.isSearching.set(true);
          return this.searchService.search(query.trim());
        }),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe((response) => {
        this.isSearching.set(false);
        if (response) this.results.set(response.results);
      });
  }

  displayFn(): string {
    return '';
  }

  onSelected(event: MatAutocompleteSelectedEvent): void {
    const result = event.option.value as SearchResult;
    this.control.setValue('', { emitEvent: false });
    this.results.set([]);
    this.router.navigateByUrl(result.link);
  }

  iconFor(type: SearchResultType): string {
    switch (type) {
      case 'property':
        return 'apartment';
      case 'unit':
        return 'door_front';
      case 'tenant':
        return 'person';
      case 'payment':
        return 'payments';
      case 'maintenance':
        return 'build';
      case 'document':
        return 'folder';
      default:
        return 'search';
    }
  }
}
