import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { debounceTime, distinctUntilChanged } from 'rxjs';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-md w-full space-y-8">
        <!-- Header -->
        <div>
          <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            🏏 PlayCricket
          </h2>
          <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Create your account
          </p>
        </div>

        <!-- Success Message -->
        <div *ngIf="registrationSuccess" class="rounded-md bg-green-50 dark:bg-green-900/20 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium text-green-800 dark:text-green-200">
                Registration successful! Please check your email to verify your account.
              </p>
              <p class="mt-2 text-sm">
                <a routerLink="/login" class="font-medium underline text-green-700 dark:text-green-300 hover:text-green-600">
                  Go to login
                </a>
              </p>
            </div>
          </div>
        </div>

        <!-- Registration Form -->
        <form *ngIf="!registrationSuccess" [formGroup]="registerForm" (ngSubmit)="onSubmit()" class="mt-8 space-y-6">
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

          <div class="rounded-md shadow-sm space-y-4">
            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email address *
              </label>
              <input
                id="email"
                formControlName="email"
                type="email"
                required
                class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800"
                placeholder="your@email.com"
                [class.border-red-500]="registerForm.get('email')?.invalid && registerForm.get('email')?.touched"
              />
              <p *ngIf="registerForm.get('email')?.invalid && registerForm.get('email')?.touched" 
                 class="mt-1 text-sm text-red-600 dark:text-red-400">
                Please enter a valid email address
              </p>
            </div>

            <!-- Full Name -->
            <div>
              <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Full Name *
              </label>
              <input
                id="name"
                formControlName="name"
                type="text"
                required
                class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800"
                placeholder="John Doe"
                [class.border-red-500]="registerForm.get('name')?.invalid && registerForm.get('name')?.touched"
              />
              <p *ngIf="registerForm.get('name')?.invalid && registerForm.get('name')?.touched" 
                 class="mt-1 text-sm text-red-600 dark:text-red-400">
                Name must be at least 2 characters
              </p>
            </div>

            <!-- Phone (optional) -->
            <div>
              <label for="phone" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Phone Number (optional)
              </label>
              <input
                id="phone"
                formControlName="phone"
                type="tel"
                class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800"
                placeholder="+1234567890"
              />
            </div>

            <!-- Password -->
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Password *
              </label>
              <input
                id="password"
                formControlName="password"
                type="password"
                required
                class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800"
                placeholder="Password"
                [class.border-red-500]="registerForm.get('password')?.invalid && registerForm.get('password')?.touched"
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
                Confirm Password *
              </label>
              <input
                id="confirmPassword"
                formControlName="confirmPassword"
                type="password"
                required
                class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800"
                placeholder="Confirm password"
                [class.border-red-500]="registerForm.errors?.['passwordMismatch'] && registerForm.get('confirmPassword')?.touched"
              />
              <p *ngIf="registerForm.errors?.['passwordMismatch'] && registerForm.get('confirmPassword')?.touched" 
                 class="mt-1 text-sm text-red-600 dark:text-red-400">
                Passwords do not match
              </p>
            </div>

            <!-- Role (optional) -->
            <div>
              <label for="role" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Role Request (optional)
              </label>
              <select
                id="role"
                formControlName="role_code"
                class="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800"
              >
                <option value="">Select a role</option>
                <option value="VIEWER">Viewer - View matches</option>
                <option value="PLAYER">Player - View team stats</option>
                <option value="SCORER">Scorer - Score matches</option>
                <option value="UMPIRE">Umpire - Officiate matches</option>
                <option value="TEAM_MANAGER">Team Manager - Manage teams</option>
              </select>
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Admin approval may be required for certain roles
              </p>
            </div>
          </div>

          <!-- Submit Button -->
          <div>
            <button
              type="submit"
              [disabled]="registerForm.invalid || isLoading"
              class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span class="absolute left-0 inset-y-0 flex items-center pl-3">
                <svg *ngIf="!isLoading" class="h-5 w-5 text-indigo-500 group-hover:text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z" />
                </svg>
                <svg *ngIf="isLoading" class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
              {{ isLoading ? 'Creating account...' : 'Create account' }}
            </button>
          </div>

          <!-- Login Link -->
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Already have an account?
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
export class RegisterComponent implements OnInit {
  registerForm: FormGroup;
  isLoading = false;
  errorMessage = '';
  registrationSuccess = false;
  passwordStrength: any = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.registerForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      name: ['', [Validators.required, Validators.minLength(2)]],
      phone: [''],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required],
      role_code: ['']
    }, { validators: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    // If already authenticated, redirect to dashboard
    if (this.authService.isAuthenticated) {
      this.router.navigate(['/']);
    }

    // Check password strength on change
    this.registerForm.get('password')?.valueChanges
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
    const password = control.get('password');
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
    if (this.registerForm.invalid) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    // Remove confirmPassword from submission
    const formData = { ...this.registerForm.value };
    delete formData.confirmPassword;

    this.authService.register(formData).subscribe({
      next: () => {
        this.registrationSuccess = true;
        this.isLoading = false;
      },
      error: (error: any) => {
        this.isLoading = false;
        this.errorMessage = error.message || 'Registration failed. Please try again.';
      }
    });
  }
}
