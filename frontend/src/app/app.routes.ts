import { Routes } from '@angular/router';
import { AuthGuard } from './core/guards/auth.guard';
import { RoleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full'
  },

  // Public Auth Routes
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'verify-email',
    loadComponent: () => import('./features/auth/verify-email/verify-email.component').then(m => m.VerifyEmailComponent)
  },
  {
    path: 'forgot-password',
    loadComponent: () => import('./features/auth/forgot-password/forgot-password.component').then(m => m.ForgotPasswordComponent)
  },
  {
    path: 'reset-password',
    loadComponent: () => import('./features/auth/reset-password/reset-password.component').then(m => m.ResetPasswordComponent)
  },
  {
    path: 'access-denied',
    loadComponent: () => import('./features/auth/access-denied/access-denied.component').then(m => m.AccessDeniedComponent)
  },

  // Protected Routes (require authentication)
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'profile',
    loadComponent: () => import('./features/user/profile/profile.component').then(m => m.ProfileComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'change-password',
    loadComponent: () => import('./features/user/change-password/change-password.component').then(m => m.ChangePasswordComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'mfa-setup',
    loadComponent: () => import('./features/user/mfa-setup/mfa-setup.component').then(m => m.MfaSetupComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'devices',
    loadComponent: () => import('./features/user/devices/devices.component').then(m => m.DevicesComponent),
    canActivate: [AuthGuard]
  },

  // Live Scoring (protected, requires SCORER, UMPIRE or ADMIN role)
  {
    path: 'live-scoring',
    loadChildren: () => import('./features/live-scoring/live-scoring.routes').then(m => m.LIVE_SCORING_ROUTES),
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['ADMIN', 'SCORER', 'UMPIRE'] }
  },

  // Temporarily commented out until components are created
  {
    path: 'teams',
    loadChildren: () => import('./features/teams/teams.routes').then(m => m.TEAMS_ROUTES),
    canActivate: [AuthGuard]
  },
  // {
  //   path: 'players',
  //   loadChildren: () => import('./features/players/players.routes').then(m => m.PLAYERS_ROUTES)
  // },
  // {
  //   path: 'venues',
  //   loadChildren: () => import('./features/venues/venues.routes').then(m => m.VENUES_ROUTES)
  // },
  // {
  //   path: 'tournaments',
  //   loadChildren: () => import('./features/tournaments/tournaments.routes').then(m => m.TOURNAMENTS_ROUTES)
  // },
  {
    path: 'matches',
    loadChildren: () => import('./features/matches/matches.routes').then(m => m.MATCHES_ROUTES),
    canActivate: [AuthGuard]
  },
  // {
  //   path: 'statistics',
  //   loadChildren: () => import('./features/statistics/statistics.routes').then(m => m.STATISTICS_ROUTES)
  // },

  // 404 Not Found
  {
    path: '**',
    loadComponent: () => import('./shared/components/not-found/not-found.component').then(m => m.NotFoundComponent)
  }
];
