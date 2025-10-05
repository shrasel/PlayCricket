import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { debounceTime, distinctUntilChanged } from 'rxjs';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-md w-full space-y-8">
        <div>
          <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            Set new password
          </h2>
          <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Please enter your new password
          </p>
        </div>

        <!-- Success Message -->
        <div *ngIf="resetSuccess" class="rounded-md bg-green-50 dark:bg-green-900/20 p-4">
          <div class="flex flex-col items-center">
            <svg class="h-16 w-16 text-green-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <h3 class="text-lg font-medium text-green-800 dark:text-green-200 mb-2">
              Password Reset Successfully!
            </h3>
            <p class="text-sm text-green-700 dark:text-green-300 text-center mb-6">
              Your password has been changed. You can now sign in with your new password.
            </p>
            <a routerLink="/login" 
               class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
              Go to Login
            </a>
          </div>
        </div>

        <!-- Form -->
        <form *ngIf="!resetSuccess" [formGroup]="resetPasswordForm" (ngSubmit)="onSubmit()" class="mt-8 space-y-6">
          <!-- Error Message -->
          <div *ngIf="errorMessage" class="rounded-md bg-red-50 dark:bg-red-900/20 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-red-800 dark:text-red-200">
                  {{ errorMessage }}
                </p>
              </div>
            </div>
          </div>

          <div class="space-y-4">
            <!-- New Password -->
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                New Password
              </label>
              <input
                id="password"
                formControlName="new_password"
                type="password"
                required
                class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800"
                placeholder="New password"
                [class.border-red-500]="resetPasswordForm.get('new_password')?.invalid && resetPasswordForm.get('new_password')?.touched"
              />
              
              <!-- Password Strength Indicator -->
              <div *ngIf="passwordStrength" class="mt-2">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-xs text-gray-600 dark:text-gray-400">Password Strength:</span>
                  <span class="text-xs font-medium" [ngClass]="{
                    'text-red-600': passwordStrength.score < 2,
                    'text-yellow-600': passwordStrength.score === 2,
                    'text-green-600': passwordStrength.score > 2
                  }">
                    {{ getStrengthLabel(passwordStrength.score) }}
                  </span>
                </div>
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    class="h-2 rounded-full transition-all duration-300"
                    [ngClass]="{
                      'bg-red-500 w-1/4': passwordStrength.score === 0,
                      'bg-red-400 w-2/4': passwordStrength.score === 1,
                      'bg-yellow-500 w-3/4': passwordStrength.score === 2,
                      'bg-green-500 w-full': passwordStrength.score >= 3
                    }"
                  ></div>
                </div>
                <ul *ngIf="passwordStrength.feedback.length > 0" class="mt-2 text-xs text-gray-600 dark:text-gray-400 space-y-1">
                  <li *ngFor="let suggestion of passwordStrength.feedback" class="flex items-start">
                    <span class="mr-1">•</span>
                    <span>{{ suggestion }}</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Confirm Password -->
            <div>
              <label for="confirmPassword" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                formControlName="confirmPassword"
                type="password"
                required
                class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800"
                placeholder="Confirm new password"
                [class.border-red-500]="resetPasswordForm.errors?.['passwordMismatch'] && resetPasswordForm.get('confirmPassword')?.touched"
              />
              <p *ngIf="resetPasswordForm.errors?.['passwordMismatch'] && resetPasswordForm.get('confirmPassword')?.touched" 
                 class="mt-1 text-sm text-red-600 dark:text-red-400">
                Passwords do not match
              </p>
            </div>
          </div>

          <div>
            <button
              type="submit"
              [disabled]="resetPasswordForm.invalid || isLoading"
              class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span class="absolute left-0 inset-y-0 flex items-center pl-3">
                <svg *ngIf="!isLoading" class="h-5 w-5 text-indigo-500 group-hover:text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                </svg>
                <svg *ngIf="isLoading" class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
              {{ isLoading ? 'Resetting...' : 'Reset password' }}
            </button>
          </div>

          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Remember your password?
              <a routerLink="/login" class="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
                Sign in
              </a>
            </p>
          </div>
        </form>
      </div>
    </div>
  `
})
export class ResetPasswordComponent implements OnInit {
  resetPasswordForm: FormGroup;
  isLoading = false;
  errorMessage = '';
  resetSuccess = false;
  passwordStrength: any = null;
  private token = '';

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {
    this.resetPasswordForm = this.fb.group({
      new_password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    // Get token from query parameters
    this.token = this.route.snapshot.queryParams['token'] || '';

    if (!this.token) {
      this.errorMessage = 'Invalid or missing reset token. Please request a new password reset.';
      return;
    }

    // Check password strength on change
    this.resetPasswordForm.get('new_password')?.valueChanges
      .pipe(
        debounceTime(300),
        distinctUntilChanged()
      )
      .subscribe(password => {
        if (password && password.length > 0) {
          this.authService.checkPasswordStrength(password).subscribe({
            next: (strength) => {
              this.passwordStrength = strength;
            },
            error: () => {
              this.passwordStrength = null;
            }
          });
        } else {
          this.passwordStrength = null;
        }
      });
  }

  passwordMatchValidator(control: AbstractControl): { [key: string]: boolean } | null {
    const password = control.get('new_password');
    const confirmPassword = control.get('confirmPassword');

    if (!password || !confirmPassword) {
      return null;
    }

    return password.value === confirmPassword.value ? null : { passwordMismatch: true };
  }

  getStrengthLabel(score: number): string {
    const labels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
    return labels[score] || 'Unknown';
  }

  onSubmit(): void {
    if (this.resetPasswordForm.invalid) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.resetPassword(this.token, this.resetPasswordForm.value.new_password).subscribe({
      next: () => {
        this.isLoading = false;
        this.resetSuccess = true;
      },
      error: (error: any) => {
        this.isLoading = false;
        this.errorMessage = error.message || 'Failed to reset password. The link may have expired.';
      }
    });
  }
}
