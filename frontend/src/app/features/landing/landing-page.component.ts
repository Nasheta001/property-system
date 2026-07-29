import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink } from '@angular/router';

interface Feature {
  icon: string;
  title: string;
  description: string;
}

@Component({
  selector: 'app-landing-page',
  imports: [RouterLink, MatButtonModule, MatIconModule],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.scss',
})
export class LandingPageComponent {
  protected readonly features: Feature[] = [
    {
      icon: 'apartment',
      title: 'Full property hierarchy',
      description: 'Model organizations, properties, buildings, floors and units exactly as they exist on the ground.',
    },
    {
      icon: 'shield',
      title: 'Tenant isolation by design',
      description: 'Every record is scoped to an organization at the database and API layer — no cross-tenant leaks.',
    },
    {
      icon: 'payments',
      title: 'Payments & ledgers',
      description: 'M-Pesa, card and bank transfer support with an immutable financial history.',
    },
    {
      icon: 'build',
      title: 'Maintenance workflows',
      description: 'From reported to closed, with contractors, priorities and full audit trails.',
    },
    {
      icon: 'insights',
      title: 'Reporting & analytics',
      description: 'Occupancy, revenue and maintenance insights across your entire portfolio.',
    },
    {
      icon: 'smart_toy',
      title: 'AI-ready architecture',
      description: 'A dedicated AI service layer for late-payment analysis, vacancy prediction and more.',
    },
  ];
}
