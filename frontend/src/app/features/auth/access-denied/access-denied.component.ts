import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-access-denied',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-md w-full space-y-8">
        <div class="text-center">
          <!-- 403 Icon -->
          <div class="flex justify-center">
            <svg class="h-24 w-24 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>

          <!-- Error Message -->
          <h1 class="mt-6 text-4xl font-extrabold text-gray-900 dark:text-white">
            403
          </h1>
          <h2 class="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
            Access Denied
          </h2>
          <p class="mt-2 text-base text-gray-600 dark:text-gray-400">
            Sorry, you don't have permission to access this page.
          </p>

          <!-- Additional Info -->
          <div class="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
            <p class="text-sm text-yellow-800 dark:text-yellow-200">
              This page requires specific roles or permissions that your account doesn't have.
              If you believe this is a mistake, please contact your administrator.
            </p>
          </div>

          <!-- Actions -->
          <div class="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              routerLink="/"
              class="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              Go to Dashboard
            </a>
            
            <button 
              (click)="goBack()"
              class="inline-flex items-center justify-center px-5 py-3 border border-gray-300 dark:border-gray-600 text-base font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Go Back
            </button>
          </div>

          <!-- Contact Support -->
          <div class="mt-8">
            <p class="text-sm text-gray-500 dark:text-gray-400">
              Need help?
              <a href="mailto:support@playcricket.com" class="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
                Contact Support
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  `
})
export class AccessDeniedComponent {
  goBack(): void {
    window.history.back();
  }
}
