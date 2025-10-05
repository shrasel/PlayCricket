import { Routes } from '@angular/router';

export const VENUES_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./venues-list/venues-list.component').then(m => m.VenuesListComponent)
  },
  {
    path: 'create',
    loadComponent: () => import('./venue-form/venue-form.component').then(m => m.VenueFormComponent)
  },
  {
    path: ':id',
    loadComponent: () => import('./venue-detail/venue-detail.component').then(m => m.VenueDetailComponent)
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./venue-form/venue-form.component').then(m => m.VenueFormComponent)
  }
];
