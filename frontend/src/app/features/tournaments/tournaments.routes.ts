import { Routes } from '@angular/router';

export const TOURNAMENTS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./tournaments-list/tournaments-list.component').then(m => m.TournamentsListComponent)
  },
  {
    path: 'create',
    loadComponent: () => import('./tournament-form/tournament-form.component').then(m => m.TournamentFormComponent)
  },
  {
    path: ':id',
    loadComponent: () => import('./tournament-detail/tournament-detail.component').then(m => m.TournamentDetailComponent)
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./tournament-form/tournament-form.component').then(m => m.TournamentFormComponent)
  }
];

