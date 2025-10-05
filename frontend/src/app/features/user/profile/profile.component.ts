import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-3xl mx-auto">
        <!-- Header -->
        <div class="mb-8">
          <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white">
            Profile Settings
          </h1>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Manage your account information and preferences
          </p>
        </div>

        <!-- Loading State -->
        <div *ngIf="isLoading && !currentUser" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div class="animate-pulse space-y-4">
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
          </div>
        </div>

        <!-- Profile Card -->
        <div *ngIf="currentUser" class="bg-white dark:bg-gray-800 shadow rounded-lg">
          <!-- User Info Section -->
          <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <!-- Avatar -->
                <div class="flex-shrink-0">
                  <div class="h-16 w-16 rounded-full bg-indigo-600 flex items-center justify-center">
                    <span class="text-2xl font-bold text-white">
                      {{ getInitials(currentUser.name) }}
                    </span>
                  </div>
                </div>
                <div>
                  <h2 class="text-xl font-bold text-gray-900 dark:text-white">
                    {{ currentUser.name }}
                  </h2>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    {{ currentUser.email }}
                  </p>
                  <!-- Status Badge -->
                  <div class="mt-1">
                    <span [ngClass]="{
                      'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400': currentUser.status === 'active',
                      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400': currentUser.status === 'pending',
                      'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': currentUser.status === 'locked'
                    }" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium">
                      {{ currentUser.status | titlecase }}
                    </span>
                    <span *ngIf="currentUser.email_verified" 
                          class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                      ✓ Email Verified
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Roles Section -->
          <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">
              Your Roles
            </h3>
            <div class="flex flex-wrap gap-2">
              <span *ngFor="let role of currentUser.roles" 
                    class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900/20 dark:text-indigo-400">
                {{ role.name }}
              </span>
              <span *ngIf="!currentUser.roles || currentUser.roles.length === 0"
                    class="text-sm text-gray-500 dark:text-gray-400">
                No roles assigned
              </span>
            </div>
          </div>

          <!-- Edit Profile Form -->
          <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Profile Information
            </h3>

            <!-- Success Message -->
            <div *ngIf="updateSuccess" class="mb-4 rounded-md bg-green-50 dark:bg-green-900/20 p-4">
              <p class="text-sm font-medium text-green-800 dark:text-green-200">
                Profile updated successfully!
              </p>
            </div>

            <!-- Error Message -->
            <div *ngIf="errorMessage" class="mb-4 rounded-md bg-red-50 dark:bg-red-900/20 p-4">
              <p class="text-sm font-medium text-red-800 dark:text-red-200">
                {{ errorMessage }}
              </p>
            </div>

            <form [formGroup]="profileForm" (ngSubmit)="updateProfile()" class="space-y-4">
              <!-- Name -->
              <div>
                <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Full Name
                </label>
                <input
                  id="name"
                  formControlName="name"
                  type="text"
                  class="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
              </div>

              <!-- Phone -->
              <div>
                <label for="phone" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Phone Number
                </label>
                <input
                  id="phone"
                  formControlName="phone"
                  type="tel"
                  class="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
              </div>

              <!-- Submit Button -->
              <div class="flex justify-end">
                <button
                  type="submit"
                  [disabled]="profileForm.invalid || profileForm.pristine || isUpdating"
                  class="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ isUpdating ? 'Saving...' : 'Save Changes' }}
                </button>
              </div>
            </form>
          </div>

          <!-- Security Settings -->
          <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Security Settings
            </h3>
            <div class="space-y-4">
              <!-- Password -->
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">Password</p>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Change your password</p>
                </div>
                <a routerLink="/change-password" 
                   class="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
                  Change
                </a>
              </div>

              <!-- MFA -->
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">Two-Factor Authentication</p>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    {{ currentUser.mfa_enabled ? 'Enabled' : 'Add extra security to your account' }}
                  </p>
                </div>
                <a routerLink="/mfa-setup" 
                   class="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
                  {{ currentUser.mfa_enabled ? 'Manage' : 'Setup' }}
                </a>
              </div>

              <!-- Active Sessions -->
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">Active Sessions</p>
                  <p class="text-sm text-gray-600 dark:text-gray-400">Manage your active devices</p>
                </div>
                <a routerLink="/devices" 
                   class="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
                  Manage
                </a>
              </div>
            </div>
          </div>

          <!-- Account Details -->
          <div class="px-6 py-5">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Account Details
            </h3>
            <dl class="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
              <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">User ID</dt>
                <dd class="mt-1 text-sm text-gray-900 dark:text-white">{{ currentUser.id }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Member Since</dt>
                <dd class="mt-1 text-sm text-gray-900 dark:text-white">
                  {{ currentUser.created_at | date:'medium' }}
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Last Updated</dt>
                <dd class="mt-1 text-sm text-gray-900 dark:text-white">
                  {{ currentUser.updated_at | date:'medium' }}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  `
})
export class ProfileComponent implements OnInit {
  currentUser: any = null;
  profileForm: FormGroup;
  isLoading = true;
  isUpdating = false;
  updateSuccess = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService
  ) {
    this.profileForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
      phone: ['']
    });
  }

  ngOnInit(): void {
    this.loadProfile();
  }

  loadProfile(): void {
    this.isLoading = true;
    this.authService.getCurrentProfile().subscribe({
      next: (user: any) => {
        this.currentUser = user;
        this.profileForm.patchValue({
          name: user.name || '',
          phone: user.phone || ''
        });
        this.isLoading = false;
      },
      error: (error: any) => {
        this.errorMessage = 'Failed to load profile';
        this.isLoading = false;
      }
    });
  }

  updateProfile(): void {
    if (this.profileForm.invalid || this.profileForm.pristine) {
      return;
    }

    this.isUpdating = true;
    this.updateSuccess = false;
    this.errorMessage = '';

    this.authService.updateProfile(this.profileForm.value).subscribe({
      next: (user: any) => {
        this.currentUser = user;
        this.profileForm.markAsPristine();
        this.isUpdating = false;
        this.updateSuccess = true;
        setTimeout(() => this.updateSuccess = false, 3000);
      },
      error: (error: any) => {
        this.isUpdating = false;
        this.errorMessage = error.message || 'Failed to update profile';
      }
    });
  }

  getInitials(name: string): string {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  }
}
