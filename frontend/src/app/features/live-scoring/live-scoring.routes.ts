import { Routes } from '@angular/router';

export const LIVE_SCORING_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./match-selector/match-selector.component').then(m => m.MatchSelectorComponent)
  },
  {
    path: ':matchId',
    loadComponent: () => import('./live-scoring-main/live-scoring-main.component').then(m => m.LiveScoringMainComponent)
  }
];
