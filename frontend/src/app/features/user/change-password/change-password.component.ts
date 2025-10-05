import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { debounceTime, distinctUntilChanged } from 'rxjs';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-md mx-auto">
        <!-- Header -->
        <div class="mb-8">
          <a routerLink="/profile" 
             class="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 mb-4">
            <svg class="mr-1 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Profile
          </a>
          <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white">
            Change Password
          </h1>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Update your account password
          </p>
        </div>

        <!-- Success Message -->
        <div *ngIf="changeSuccess" class="mb-4 rounded-md bg-green-50 dark:bg-green-900/20 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium text-green-800 dark:text-green-200">
                Password changed successfully!
              </p>
              <p class="mt-2 text-sm">
                <a routerLink="/profile" class="font-medium underline text-green-700 dark:text-green-300 hover:text-green-600">
                  Back to Profile
                </a>
              </p>
            </div>
          </div>
        </div>

        <!-- Form Card -->
        <div *ngIf="!changeSuccess" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <!-- Error Message -->
          <div *ngIf="errorMessage" class="mb-4 rounded-md bg-red-50 dark:bg-red-900/20 p-4">
            <p class="text-sm font-medium text-red-800 dark:text-red-200">
              {{ errorMessage }}
            </p>
          </div>

          <form [formGroup]="passwordForm" (ngSubmit)="onSubmit()" class="space-y-6">
            <!-- Current Password -->
            <div>
              <label for="currentPassword" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Current Password *
              </label>
              <input
                id="currentPassword"
                formControlName="current_password"
                type="password"
                required
                class="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                placeholder="Enter current password"
                [class.border-red-500]="passwordForm.get('current_password')?.invalid && passwordForm.get('current_password')?.touched"
              />
              <p *ngIf="passwordForm.get('current_password')?.invalid && passwordForm.get('current_password')?.touched" 
                 class="mt-1 text-sm text-red-600 dark:text-red-400">
                Current password is required
              </p>
            </div>

            <!-- New Password -->
            <div>
              <label for="newPassword" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                New Password *
              </label>
              <input
                id="newPassword"
                formControlName="new_password"
                type="password"
                required
                class="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                placeholder="Enter new password"
                [class.border-red-500]="passwordForm.get('new_password')?.invalid && passwordForm.get('new_password')?.touched"
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

            <!-- Confirm New Password -->
            <div>
              <label for="confirmPassword" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirm New Password *
              </label>
              <input
                id="confirmPassword"
                formControlName="confirm_password"
                type="password"
                required
                class="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                placeholder="Confirm new password"
                [class.border-red-500]="passwordForm.errors?.['passwordMismatch'] && passwordForm.get('confirm_password')?.touched"
              />
              <p *ngIf="passwordForm.errors?.['passwordMismatch'] && passwordForm.get('confirm_password')?.touched" 
                 class="mt-1 text-sm text-red-600 dark:text-red-400">
                Passwords do not match
              </p>
            </div>

            <!-- Submit Button -->
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                (click)="goBack()"
                class="px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                [disabled]="passwordForm.invalid || isLoading"
                class="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ isLoading ? 'Changing...' : 'Change Password' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `
})
export class ChangePasswordComponent implements OnInit {
  passwordForm: FormGroup;
  isLoading = false;
  errorMessage = '';
  changeSuccess = false;
  passwordStrength: any = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.passwordForm = this.fb.group({
      current_password: ['', Validators.required],
      new_password: ['', [Validators.required, Validators.minLength(8)]],
      confirm_password: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    // Check password strength on change
    this.passwordForm.get('new_password')?.valueChanges
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
    const newPassword = control.get('new_password');
    const confirmPassword = control.get('confirm_password');

    if (!newPassword || !confirmPassword) {
      return null;
    }

    return newPassword.value === confirmPassword.value ? null : { passwordMismatch: true };
  }

  getStrengthLabel(score: number): string {
    const labels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
    return labels[score] || 'Unknown';
  }

  onSubmit(): void {
    if (this.passwordForm.invalid) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const { current_password, new_password } = this.passwordForm.value;

    this.authService.changePassword(current_password, new_password).subscribe({
      next: () => {
        this.isLoading = false;
        this.changeSuccess = true;
      },
      error: (error: any) => {
        this.isLoading = false;
        this.errorMessage = error.message || 'Failed to change password';
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/profile']);
  }
}
