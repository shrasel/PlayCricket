import { Routes } from '@angular/router';

export const TEAMS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./teams-list/teams-list.component').then(m => m.TeamsListComponent)
  },
  {
    path: 'create',
    loadComponent: () => import('./team-form/team-form.component').then(m => m.TeamFormComponent)
  },
  {
    path: ':id',
    loadComponent: () => import('./team-detail/team-detail.component').then(m => m.TeamDetailComponent)
  },
  {
    path: ':id/edit',
    loadComponent: () => import('./team-form/team-form.component').then(m => m.TeamFormComponent)
  }
];
