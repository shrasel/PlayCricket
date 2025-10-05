import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

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
            <span class="text-xl font-bold text-primary-600">PlayCricket</span>
          </a>

          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center space-x-6">
            <a routerLink="/dashboard" routerLinkActive="text-primary-600" [routerLinkActiveOptions]="{exact: false}" 
               class="hover:text-primary-600 transition-colors">
              Dashboard
            </a>
            <a routerLink="/matches" routerLinkActive="text-primary-600" 
               class="hover:text-primary-600 transition-colors">
              Matches
            </a>
            <a routerLink="/live-scoring" routerLinkActive="text-primary-600"
               class="hover:text-primary-600 transition-colors">
              Live Scoring
            </a>
            <a routerLink="/teams" routerLinkActive="text-primary-600" 
               class="hover:text-primary-600 transition-colors">
              Teams
            </a>
            <a routerLink="/players" routerLinkActive="text-primary-600" 
               class="hover:text-primary-600 transition-colors">
              Players
            </a>
            <a routerLink="/statistics" routerLinkActive="text-primary-600" 
               class="hover:text-primary-600 transition-colors">
              Statistics
            </a>
            <button (click)="toggleDarkMode()" 
                    class="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700">
              {{ isDarkMode ? '☀️' : '🌙' }}
            </button>
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
            <a routerLink="/dashboard" (click)="closeMobileMenu()" 
               class="block py-2 hover:text-primary-600">Dashboard</a>
            <a routerLink="/matches" (click)="closeMobileMenu()" 
               class="block py-2 hover:text-primary-600">Matches</a>
            <a routerLink="/live-scoring" (click)="closeMobileMenu()" 
               class="block py-2 hover:text-primary-600">Live Scoring</a>
            <a routerLink="/teams" (click)="closeMobileMenu()" 
               class="block py-2 hover:text-primary-600">Teams</a>
            <a routerLink="/players" (click)="closeMobileMenu()" 
               class="block py-2 hover:text-primary-600">Players</a>
            <a routerLink="/statistics" (click)="closeMobileMenu()" 
               class="block py-2 hover:text-primary-600">Statistics</a>
          </div>
        }
      </nav>
    </header>
  `,
  styles: []
})
export class HeaderComponent {
  isMobileMenuOpen = false;
  isDarkMode = false;

  ngOnInit() {
    // Check for saved dark mode preference
    this.isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (this.isDarkMode) {
      document.documentElement.classList.add('dark');
    }
  }

  toggleMobileMenu() {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
  }

  closeMobileMenu() {
    this.isMobileMenuOpen = false;
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
