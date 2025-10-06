import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService, User } from '../../../core/services/auth.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  template: `
    <header class="bg-white dark:bg-gray-800 shadow-md">
      <nav class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <!-- Logo -->
          <a routerLink="/" class="flex items-center space-x-2">
            <span class="text-2xl">🏏</span>
            <span class="text-xl font-bold text-indigo-600 dark:text-indigo-400">PlayCricket</span>
          </a>

          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center space-x-6">
            @if (isAuthenticated && currentUser) {
              <a routerLink="/dashboard" routerLinkActive="text-indigo-600 dark:text-indigo-400" [routerLinkActiveOptions]="{exact: false}" 
                 class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                Dashboard
              </a>
              <a routerLink="/tournaments" routerLinkActive="text-indigo-600 dark:text-indigo-400" 
                 class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                Tournaments
              </a>
              <a routerLink="/matches" routerLinkActive="text-indigo-600 dark:text-indigo-400" 
                 class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                Matches
              </a>
              <a routerLink="/live-scoring" routerLinkActive="text-indigo-600 dark:text-indigo-400"
                 class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                Live Scoring
              </a>
              <a routerLink="/teams" routerLinkActive="text-indigo-600 dark:text-indigo-400" 
                 class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                Teams
              </a>
              <a routerLink="/players" routerLinkActive="text-indigo-600 dark:text-indigo-400" 
                 class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                Players
              </a>
              <a routerLink="/venues" routerLinkActive="text-indigo-600 dark:text-indigo-400" 
                 class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                Venues
              </a>
              <a routerLink="/statistics" routerLinkActive="text-indigo-600 dark:text-indigo-400" 
                 class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                Statistics
              </a>
              
              <!-- Dark Mode Toggle -->
              <button (click)="toggleDarkMode()" 
                      class="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700">
                {{ isDarkMode ? '☀️' : '🌙' }}
              </button>

              <!-- User Profile Dropdown -->
              <div class="relative user-menu-container">
                <button 
                  (click)="toggleUserMenu(); $event.stopPropagation()"
                  type="button"
                  class="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-all duration-200 group">
                  <!-- Avatar with gradient border -->
                  <div class="relative">
                    <div class="absolute inset-0 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 opacity-75 blur-sm group-hover:opacity-100 transition-opacity"></div>
                    <div class="relative h-9 w-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center ring-2 ring-white dark:ring-gray-800">
                      <span class="text-sm font-bold text-white">{{ getInitials(currentUser.name) }}</span>
                    </div>
                  </div>
                  
                  <!-- Name and chevron -->
                  <div class="hidden lg:flex items-center space-x-2">
                    <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ currentUser.name }}</span>
                    <svg 
                      class="h-4 w-4 text-gray-400 transition-transform duration-200"
                      [class.rotate-180]="isUserMenuOpen"
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </button>

                <!-- Modern Dropdown Menu -->
                @if (isUserMenuOpen) {
                  <div class="absolute right-0 mt-3 w-72 rounded-xl shadow-2xl bg-white dark:bg-gray-800 ring-1 ring-black/5 dark:ring-white/10 z-50 overflow-hidden animate-slideDown">
                    <!-- User Info Header with gradient -->
                    <div class="relative bg-gradient-to-br from-indigo-500 to-purple-600 px-4 py-4">
                      <div class="absolute inset-0 bg-black/10"></div>
                      <div class="relative flex items-center space-x-3">
                        <div class="h-12 w-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center ring-2 ring-white/50">
                          <span class="text-lg font-bold text-white">{{ getInitials(currentUser.name) }}</span>
                        </div>
                        <div class="flex-1 min-w-0">
                          <p class="text-sm font-semibold text-white truncate">{{ currentUser.name }}</p>
                          <p class="text-xs text-white/80 truncate">{{ currentUser.email }}</p>
                        </div>
                      </div>
                      
                      <!-- Roles badges -->
                      <div class="relative mt-3 flex flex-wrap gap-1.5">
                        <span *ngFor="let role of currentUser.roles" 
                              class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-white/20 backdrop-blur-sm text-white border border-white/30">
                          {{ role }}
                        </span>
                      </div>
                    </div>

                    <!-- Menu Items -->
                    <div class="py-2">
                      <a 
                        routerLink="/profile" 
                        (click)="closeUserMenu(); $event.stopPropagation()"
                        class="flex items-center px-4 py-2.5 text-sm text-gray-700 dark:text-gray-200 hover:bg-indigo-50 dark:hover:bg-gray-700/50 transition-colors group">
                        <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 group-hover:scale-110 transition-transform">
                          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                        </div>
                        <div class="ml-3">
                          <p class="font-medium">Your Profile</p>
                          <p class="text-xs text-gray-500 dark:text-gray-400">View and edit your information</p>
                        </div>
                      </a>
                      
                      <a 
                        routerLink="/change-password" 
                        (click)="closeUserMenu(); $event.stopPropagation()"
                        class="flex items-center px-4 py-2.5 text-sm text-gray-700 dark:text-gray-200 hover:bg-indigo-50 dark:hover:bg-gray-700/50 transition-colors group">
                        <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 group-hover:scale-110 transition-transform">
                          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                          </svg>
                        </div>
                        <div class="ml-3">
                          <p class="font-medium">Change Password</p>
                          <p class="text-xs text-gray-500 dark:text-gray-400">Update your password</p>
                        </div>
                      </a>

                      <div class="my-2 border-t border-gray-200 dark:border-gray-700"></div>

                      <button 
                        (click)="logout(); $event.stopPropagation()"
                        type="button"
                        class="flex items-center w-full text-left px-4 py-2.5 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors group">
                        <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 group-hover:scale-110 transition-transform">
                          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                          </svg>
                        </div>
                        <div class="ml-3">
                          <p class="font-medium">Sign Out</p>
                          <p class="text-xs text-gray-500 dark:text-gray-400">Logout from your account</p>
                        </div>
                      </button>
                    </div>
                  </div>
                }
              </div>
            } @else {
              <a routerLink="/login" 
                 class="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400">
                Sign in
              </a>
              <a routerLink="/register"
                 class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                Sign up
              </a>
            }
          </div>

          <!-- Mobile Menu Button -->
          <button (click)="toggleMobileMenu()" class="md:hidden p-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>

        <!-- Mobile Navigation -->
        @if (isMobileMenuOpen) {
          <div class="md:hidden mt-4 space-y-2">
            @if (isAuthenticated && currentUser) {
              <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700 mb-2">
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ currentUser.name }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{{ currentUser.email }}</p>
              </div>
                          @if (isAuthenticated && currentUser) {
              <a routerLink="/dashboard" (click)="closeMobileMenu()" 
                 class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">Dashboard</a>
              <a routerLink="/tournaments" (click)="closeMobileMenu()" 
                 class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">Tournaments</a>
              <a routerLink="/matches" (click)="closeMobileMenu()" 
                 class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">Matches</a>
              <a routerLink="/live-scoring" (click)="closeMobileMenu()" 
                 class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">Live Scoring</a>
              <a routerLink="/teams" (click)="closeMobileMenu()" 
                 class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">Teams</a>
              <a routerLink="/players" (click)="closeMobileMenu()" 
                 class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">Players</a>
              <a routerLink="/venues" (click)="closeMobileMenu()" 
                 class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">Venues</a>
              <a routerLink="/statistics" (click)="closeMobileMenu()" 
                 class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">Statistics</a>
              
              <div class="border-t border-gray-200 dark:border-gray-700 my-2"></div>
              
              <a routerLink="/profile" (click)="closeMobileMenu()" 
                 class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">Your Profile</a>
              <a routerLink="/change-password" (click)="closeMobileMenu()" 
                 class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">Change Password</a>
              
              <button (click)="logout()"
                      class="w-full text-left py-2 px-4 text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                Sign out
              </button>
            } @else {
              <a routerLink="/login" (click)="closeMobileMenu()"
                 class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">Sign in</a>
              <a routerLink="/register" (click)="closeMobileMenu()"
                 class="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">Sign up</a>
            }
          </div>
        }
      </nav>
    </header>
  `,
  styles: [`
    @keyframes slideDown {
      from {
        opacity: 0;
        transform: translateY(-10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .animate-slideDown {
      animation: slideDown 0.2s ease-out;
    }

    /* Smooth transitions */
    * {
      transition-property: background-color, border-color, color, fill, stroke;
      transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
      transition-duration: 150ms;
    }
  `]
})
export class HeaderComponent implements OnInit, OnDestroy {
  isMobileMenuOpen = false;
  isUserMenuOpen = false;
  isDarkMode = false;
  isAuthenticated = false;
  currentUser: User | null = null;
  private destroy$ = new Subject<void>();

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    // Check for saved dark mode preference
    this.isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (this.isDarkMode) {
      document.documentElement.classList.add('dark');
    }

    // Subscribe to authentication state
    this.authService.isAuthenticated$
      .pipe(takeUntil(this.destroy$))
      .subscribe(isAuth => {
        this.isAuthenticated = isAuth;
      });

    // Subscribe to current user
    this.authService.currentUser$
      .pipe(takeUntil(this.destroy$))
      .subscribe(user => {
        this.currentUser = user;
      });

    // Close dropdown when clicking outside
    document.addEventListener('click', this.handleClickOutside.bind(this));
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    document.removeEventListener('click', this.handleClickOutside.bind(this));
  }

  handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (this.isUserMenuOpen && !target.closest('.user-menu-container')) {
      this.isUserMenuOpen = false;
    }
  }

  toggleMobileMenu() {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
  }

  closeMobileMenu() {
    this.isMobileMenuOpen = false;
  }

  toggleUserMenu() {
    this.isUserMenuOpen = !this.isUserMenuOpen;
  }

  closeUserMenu() {
    this.isUserMenuOpen = false;
  }

  getInitials(name: string): string {
    if (!name) return '?';
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }

  logout() {
    console.log('🚪 Logout initiated...');
    this.closeUserMenu();
    this.closeMobileMenu();
    
    this.authService.logout().subscribe({
      next: () => {
        console.log('✅ Logout successful, redirecting to login');
        this.router.navigate(['/login']);
      },
      error: (err) => {
        console.error('❌ Logout error:', err);
        // Even if logout fails on backend, clear local state
        this.router.navigate(['/login']);
      }
    });
  }

  toggleDarkMode() {
    this.isDarkMode = !this.isDarkMode;
    if (this.isDarkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('darkMode', 'true');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('darkMode', 'false');
    }
  }
}
