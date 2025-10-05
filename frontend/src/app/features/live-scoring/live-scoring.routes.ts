import { Routes } from '@angular/router';

export const LIVE_SCORING_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./live-scoring/live-scoring.component').then(m => m.LiveScoringComponent)
  },
  {
    path: ':matchId',
    loadComponent: () => import('./live-scoring/live-scoring.component').then(m => m.LiveScoringComponent)
  }
];
