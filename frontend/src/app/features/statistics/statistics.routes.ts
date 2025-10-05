import { Routes } from '@angular/router';

export const STATISTICS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./statistics-dashboard/statistics-dashboard.component').then(m => m.StatisticsDashboardComponent)
  },
  {
    path: 'match/:id',
    loadComponent: () => import('./match-scorecard/match-scorecard.component').then(m => m.MatchScorecardComponent)
  },
  {
    path: 'player/:id',
    loadComponent: () => import('./player-stats/player-stats.component').then(m => m.PlayerStatsComponent)
  }
];
