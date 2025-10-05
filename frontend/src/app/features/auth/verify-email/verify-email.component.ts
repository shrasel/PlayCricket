import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-verify-email',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-md w-full space-y-8">
        <div class="text-center">
          <h2 class="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            Email Verification
          </h2>
        </div>

        <!-- Loading State -->
        <div *ngIf="isVerifying" class="text-center">
          <div class="inline-flex items-center justify-center">
            <svg class="animate-spin h-12 w-12 text-indigo-600" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Verifying your email...</p>
        </div>

        <!-- Success State -->
        <div *ngIf="verificationSuccess" class="rounded-md bg-green-50 dark:bg-green-900/20 p-6">
          <div class="flex flex-col items-center">
            <svg class="h-16 w-16 text-green-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <h3 class="text-lg font-medium text-green-800 dark:text-green-200 mb-2">
              Email Verified Successfully!
            </h3>
            <p class="text-sm text-green-700 dark:text-green-300 text-center mb-6">
              Your email has been verified. You can now sign in to your account.
            </p>
            <a routerLink="/login" 
               class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
              Go to Login
            </a>
          </div>
        </div>

        <!-- Error State -->
        <div *ngIf="errorMessage" class="rounded-md bg-red-50 dark:bg-red-900/20 p-6">
          <div class="flex flex-col items-center">
            <svg class="h-16 w-16 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <h3 class="text-lg font-medium text-red-800 dark:text-red-200 mb-2">
              Verification Failed
            </h3>
            <p class="text-sm text-red-700 dark:text-red-300 text-center mb-6">
              {{ errorMessage }}
            </p>
            <div class="flex space-x-4">
              <a routerLink="/login" 
                 class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                Back to Login
              </a>
              <button (click)="resendVerification()" 
                      [disabled]="isResending"
                      class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
                {{ isResending ? 'Sending...' : 'Resend Email' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class VerifyEmailComponent implements OnInit {
  isVerifying = false;
  isResending = false;
  verificationSuccess = false;
  errorMessage = '';
  private token = '';
  private email = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    // Get token from query parameters
    this.token = this.route.snapshot.queryParams['token'] || '';
    this.email = this.route.snapshot.queryParams['email'] || '';

    if (!this.token) {
      this.errorMessage = 'Invalid verification link. Please check your email and try again.';
      return;
    }

    // Automatically verify email
    this.verifyEmail();
  }

  verifyEmail(): void {
    this.isVerifying = true;
    this.errorMessage = '';

    this.authService.verifyEmail(this.token).subscribe({
      next: () => {
        this.isVerifying = false;
        this.verificationSuccess = true;
      },
      error: (error: any) => {
        this.isVerifying = false;
        this.errorMessage = error.message || 'Email verification failed. The link may have expired.';
      }
    });
  }

  resendVerification(): void {
    if (!this.email) {
      this.errorMessage = 'Email address not found. Please try registering again.';
      return;
    }

    this.isResending = true;

    this.authService.resendVerificationEmail(this.email).subscribe({
      next: () => {
        this.isResending = false;
        this.errorMessage = '';
        alert('Verification email sent! Please check your inbox.');
      },
      error: (error: any) => {
        this.isResending = false;
        alert(error.message || 'Failed to resend verification email');
      }
    });
  }
}
