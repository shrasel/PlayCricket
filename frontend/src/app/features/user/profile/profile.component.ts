import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService, User } from '../../../core/services/auth.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 py-8 px-4 sm:px-6 lg:px-8">
      <div class="max-w-5xl mx-auto">
        
        <!-- Header with breadcrumb -->
        <div class="mb-6">
          <nav class="flex mb-4" aria-label="Breadcrumb">
            <ol class="inline-flex items-center space-x-1 md:space-x-3">
              <li class="inline-flex items-center">
                <a routerLink="/dashboard" class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-white">
                  <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>
                  </svg>
                  Dashboard
                </a>
              </li>
              <li>
                <div class="flex items-center">
                  <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                  </svg>
                  <span class="ml-1 text-sm font-medium text-gray-500 dark:text-gray-400">Profile</span>
                </div>
              </li>
            </ol>
          </nav>
          
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
                My Profile
              </h1>
              <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                Manage your personal information and account settings
              </p>
            </div>
            <a routerLink="/change-password" 
               class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm hover:shadow-md transition-all">
              <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
              Change Password
            </a>
          </div>
        </div>

        <!-- Loading State -->
        <div *ngIf="isLoading && !currentUser" class="bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-8">
          <div class="animate-pulse space-y-6">
            <div class="flex items-center space-x-4">
              <div class="h-24 w-24 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
              <div class="flex-1 space-y-3">
                <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
                <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              </div>
            </div>
            <div class="space-y-3">
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
              <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-4/6"></div>
            </div>
          </div>
        </div>

        <!-- Error State -->
        <div *ngIf="!isLoading && !currentUser && errorMessage" class="bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-8">
          <div class="text-center">
            <svg class="mx-auto h-16 w-16 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">
              Failed to Load Profile
            </h3>
            <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {{ errorMessage }}
            </p>
            <div class="mt-6">
              <a routerLink="/login" 
                 class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm">
                Go to Login
              </a>
            </div>
          </div>
        </div>

        <!-- Profile Content -->
        <div *ngIf="!isLoading && currentUser" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          <!-- Left Sidebar - User Card -->
          <div class="lg:col-span-1">
            <div class="bg-white dark:bg-gray-800 shadow-xl rounded-2xl overflow-hidden">
              <!-- Profile Header with Gradient -->
              <div class="relative h-32 bg-gradient-to-r from-indigo-500 to-purple-600">
                <div class="absolute inset-0 bg-black/10"></div>
              </div>
              
              <!-- Avatar -->
              <div class="relative px-6 pb-6">
                <div class="flex flex-col items-center -mt-16">
                  <div class="relative">
                    <div class="h-32 w-32 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 p-1 shadow-2xl">
                      <div class="h-full w-full rounded-full bg-white dark:bg-gray-800 flex items-center justify-center">
                        <span class="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                          {{ getInitials(currentUser.name) }}
                        </span>
                      </div>
                    </div>
                    <!-- Status Indicator -->
                    <div class="absolute bottom-2 right-2">
                      <span [ngClass]="{
                        'bg-green-500': currentUser.status === 'active',
                        'bg-yellow-500': currentUser.status === 'pending',
                        'bg-red-500': currentUser.status === 'locked'
                      }" class="block h-4 w-4 rounded-full border-2 border-white dark:border-gray-800"></span>
                    </div>
                  </div>
                  
                  <div class="mt-4 text-center">
                    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
                      {{ currentUser.name }}
                    </h2>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {{ currentUser.email }}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                      ID: #{{ currentUser.id }}
                    </p>
                  </div>

                  <!-- Badges -->
                  <div class="mt-4 flex flex-wrap justify-center gap-2">
                    <span [ngClass]="{
                      'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400': currentUser.status === 'active',
                      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400': currentUser.status === 'pending',
                      'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400': currentUser.status === 'locked'
                    }" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium">
                      <svg class="mr-1 h-3 w-3" fill="currentColor" viewBox="0 0 8 8">
                        <circle cx="4" cy="4" r="3" />
                      </svg>
                      {{ currentUser.status | titlecase }}
                    </span>
                    
                    <span *ngIf="currentUser.is_email_verified" 
                          class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                      <svg class="mr-1 h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                      Verified
                    </span>
                  </div>

                  <!-- Roles -->
                  <div class="mt-6 w-full">
                    <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                      Assigned Roles
                    </h3>
                    <div class="flex flex-wrap gap-2">
                      <span *ngFor="let role of currentUser.roles" 
                            class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
                        <svg class="mr-1.5 h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                        </svg>
                        {{ role }}
                      </span>
                      <span *ngIf="!currentUser.roles || currentUser.roles.length === 0"
                            class="text-sm text-gray-500 dark:text-gray-400 italic">
                        No roles assigned
                      </span>
                    </div>
                  </div>

                  <!-- Stats -->
                  <div class="mt-6 w-full grid grid-cols-2 gap-4">
                    <div class="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                      <div class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                        {{ daysSinceJoined }}
                      </div>
                      <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        Days Active
                      </div>
                    </div>
                    <div class="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                      <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
                        {{ currentUser.mfa_enabled ? 'ON' : 'OFF' }}
                      </div>
                      <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        2FA Status
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Actions Card -->
            <div class="mt-6 bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-6">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">
                Quick Actions
              </h3>
              <div class="space-y-2">
                <a routerLink="/change-password" 
                   class="flex items-center p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors group">
                  <div class="flex items-center justify-center w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 group-hover:scale-110 transition-transform">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                    </svg>
                  </div>
                  <div class="ml-3 flex-1">
                    <p class="text-sm font-medium text-gray-900 dark:text-white">Change Password</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">Update your password</p>
                  </div>
                  <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </a>
              </div>
            </div>
          </div>

          <!-- Right Content - Profile Details & Edit Form -->
          <div class="lg:col-span-2 space-y-6">
            
            <!-- Edit Profile Form -->
            <div class="bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-6">
              <div class="flex items-center justify-between mb-6">
                <div>
                  <h2 class="text-xl font-bold text-gray-900 dark:text-white">
                    Edit Profile
                  </h2>
                  <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    Update your personal information
                  </p>
                </div>
              </div>

              <!-- Success Message -->
              <div *ngIf="updateSuccess" 
                   class="mb-6 rounded-lg bg-green-50 dark:bg-green-900/20 p-4 border border-green-200 dark:border-green-800">
                <div class="flex">
                  <svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <p class="ml-3 text-sm font-medium text-green-800 dark:text-green-200">
                    Profile updated successfully!
                  </p>
                </div>
              </div>

              <!-- Error Message -->
              <div *ngIf="errorMessage" 
                   class="mb-6 rounded-lg bg-red-50 dark:bg-red-900/20 p-4 border border-red-200 dark:border-red-800">
                <div class="flex">
                  <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                  <p class="ml-3 text-sm font-medium text-red-800 dark:text-red-200">
                    {{ errorMessage }}
                  </p>
                </div>
              </div>

              <form [formGroup]="profileForm" (ngSubmit)="updateProfile()" class="space-y-6">
                <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <!-- Name -->
                  <div class="sm:col-span-2">
                    <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Full Name *
                    </label>
                    <div class="relative">
                      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                      </div>
                      <input
                        id="name"
                        formControlName="name"
                        type="text"
                        placeholder="Enter your full name"
                        class="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-all"
                      />
                    </div>
                    <p *ngIf="profileForm.get('name')?.invalid && profileForm.get('name')?.touched" 
                       class="mt-2 text-sm text-red-600 dark:text-red-400">
                      Name must be at least 2 characters long
                    </p>
                  </div>

                  <!-- Email (Read-only) -->
                  <div>
                    <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Email Address
                    </label>
                    <div class="relative">
                      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <input
                        id="email"
                        type="email"
                        [value]="currentUser.email"
                        disabled
                        class="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm bg-gray-50 dark:bg-gray-700/50 text-gray-500 dark:text-gray-400 cursor-not-allowed sm:text-sm"
                      />
                    </div>
                    <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      Email cannot be changed
                    </p>
                  </div>

                  <!-- Phone -->
                  <div>
                    <label for="phone" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Phone Number
                    </label>
                    <div class="relative">
                      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                        </svg>
                      </div>
                      <input
                        id="phone"
                        formControlName="phone"
                        type="tel"
                        placeholder="+1 (555) 000-0000"
                        class="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-all"
                      />
                    </div>
                  </div>
                </div>

                <!-- Submit Buttons -->
                <div class="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <button
                    type="button"
                    (click)="resetForm()"
                    [disabled]="profileForm.pristine || isUpdating"
                    class="px-4 py-2.5 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-lg text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    Reset
                  </button>
                  <button
                    type="submit"
                    [disabled]="profileForm.invalid || profileForm.pristine || isUpdating"
                    class="px-6 py-2.5 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transition-all flex items-center"
                  >
                    <svg *ngIf="isUpdating" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ isUpdating ? 'Saving Changes...' : 'Save Changes' }}
                  </button>
                </div>
              </form>
            </div>

            <!-- Account Information -->
            <div class="bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-6">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">
                Account Information
              </h2>
              
              <dl class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div class="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-100 dark:border-blue-800">
                  <dt class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">
                    User ID
                  </dt>
                  <dd class="text-lg font-semibold text-gray-900 dark:text-white font-mono">
                    #{{ currentUser.id }}
                  </dd>
                </div>

                <div class="p-4 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-100 dark:border-green-800">
                  <dt class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">
                    Account Status
                  </dt>
                  <dd class="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                    {{ currentUser.status }}
                  </dd>
                </div>

                <div class="p-4 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg border border-purple-100 dark:border-purple-800">
                  <dt class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">
                    Member Since
                  </dt>
                  <dd class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ currentUser.created_at | date:'mediumDate' }}
                  </dd>
                  <dd class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    {{ currentUser.created_at | date:'shortTime' }}
                  </dd>
                </div>

                <div class="p-4 bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 rounded-lg border border-orange-100 dark:border-orange-800">
                  <dt class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">
                    Last Login
                  </dt>
                  <dd class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ currentUser.last_login_at ? (currentUser.last_login_at | date:'mediumDate') : 'Never' }}
                  </dd>
                  <dd class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    {{ currentUser.last_login_at ? (currentUser.last_login_at | date:'shortTime') : '' }}
                  </dd>
                </div>
              </dl>
            </div>

            <!-- Security Overview -->
            <div class="bg-white dark:bg-gray-800 shadow-xl rounded-2xl p-6">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">
                Security & Privacy
              </h2>
              
              <div class="space-y-4">
                <!-- Email Verification -->
                <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                  <div class="flex items-center space-x-3">
                    <div [ngClass]="currentUser.is_email_verified ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400'" 
                         class="flex items-center justify-center w-10 h-10 rounded-lg">
                      <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"></path>
                        <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"></path>
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900 dark:text-white">
                        Email Verification
                      </p>
                      <p class="text-xs text-gray-600 dark:text-gray-400">
                        {{ currentUser.is_email_verified ? 'Your email is verified' : 'Please verify your email' }}
                      </p>
                    </div>
                  </div>
                  <span [ngClass]="currentUser.is_email_verified ? 'text-green-600 dark:text-green-400' : 'text-yellow-600 dark:text-yellow-400'" 
                        class="text-sm font-semibold">
                    {{ currentUser.is_email_verified ? 'Verified' : 'Pending' }}
                  </span>
                </div>

                <!-- Two-Factor Authentication -->
                <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group cursor-pointer">
                  <div class="flex items-center space-x-3">
                    <div [ngClass]="currentUser.mfa_enabled ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-400'" 
                         class="flex items-center justify-center w-10 h-10 rounded-lg group-hover:scale-110 transition-transform">
                      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900 dark:text-white">
                        Two-Factor Authentication (2FA)
                      </p>
                      <p class="text-xs text-gray-600 dark:text-gray-400">
                        {{ currentUser.mfa_enabled ? 'Extra security is enabled' : 'Add an extra layer of security' }}
                      </p>
                    </div>
                  </div>
                  <a routerLink="/mfa-setup" 
                     class="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
                    {{ currentUser.mfa_enabled ? 'Manage' : 'Enable' }} →
                  </a>
                </div>

                <!-- Password -->
                <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group cursor-pointer">
                  <div class="flex items-center space-x-3">
                    <div class="flex items-center justify-center w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 group-hover:scale-110 transition-transform">
                      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900 dark:text-white">
                        Password
                      </p>
                      <p class="text-xs text-gray-600 dark:text-gray-400">
                        Last changed {{ daysSincePasswordChange }} days ago
                      </p>
                    </div>
                  </div>
                  <a routerLink="/change-password" 
                     class="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
                    Change →
                  </a>
                </div>
              </div>
            </div>
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
    private authService: AuthService,
    private router: Router
  ) {
    this.profileForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
      phone: ['']
    });
  }

  ngOnInit(): void {
    // Check if user is actually authenticated before loading profile
    console.log('🔍 Profile component initialized');
    console.log('  - Token exists:', !!this.authService.token);
    console.log('  - Token value:', this.authService.token?.substring(0, 30) + '...');
    
    // Use a simple synchronous check first
    if (!this.authService.token) {
      console.warn('⚠️ No token found! User is not authenticated.');
      this.errorMessage = 'You are not logged in. Please login to view your profile.';
      this.isLoading = false;
      
      setTimeout(() => {
        this.router.navigate(['/login'], { 
          queryParams: { returnUrl: '/profile' } 
        });
      }, 2000);
      return;
    }
    
    console.log('✅ Token found, loading profile...');
    // User has token, load profile
    this.loadProfile();
  }

  get daysSinceJoined(): number {
    if (!this.currentUser?.created_at) return 0;
    const created = new Date(this.currentUser.created_at);
    const now = new Date();
    return Math.floor((now.getTime() - created.getTime()) / (1000 * 60 * 60 * 24));
  }

  get daysSincePasswordChange(): number {
    // Mock value - replace with actual password change date when available
    return 45;
  }

  loadProfile(): void {
    this.isLoading = true;
    this.errorMessage = '';
    
    console.log('📱 Loading profile...');
    
    this.authService.getCurrentProfile().subscribe({
      next: (user: User) => {
        console.log('✅ Profile loaded:', user);
        this.currentUser = user;
        this.profileForm.patchValue({
          name: user.name || '',
          phone: user.phone || ''
        });
        this.isLoading = false;
      },
      error: (error: any) => {
        console.error('❌ Failed to load profile:', error);
        
        // If 401/403, try to refresh the session first
        if (error.status === 403 || error.status === 401) {
          console.log('🔄 Authentication failed, attempting session restore...');
          
          this.authService.restoreSession().then(() => {
            console.log('🔄 Session restore complete, retrying profile load...');
            
            // Retry loading profile after session restore
            this.authService.getCurrentProfile().subscribe({
              next: (user: User) => {
                console.log('✅ Profile loaded after session restore:', user);
                this.currentUser = user;
                this.profileForm.patchValue({
                  name: user.name || '',
                  phone: user.phone || ''
                });
                this.isLoading = false;
              },
              error: (retryError: any) => {
                console.error('❌ Profile load failed even after session restore:', retryError);
                this.errorMessage = 'You are not logged in. Redirecting to login...';
                this.isLoading = false;
                
                // Redirect to login after a short delay
                setTimeout(() => {
                  window.location.href = '/login';
                }, 2000);
              }
            });
          });
        } else {
          this.errorMessage = error.error?.detail || 'Failed to load profile. Please try again.';
          this.isLoading = false;
        }
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
      next: (user: User) => {
        this.currentUser = user;
        this.profileForm.patchValue({
          name: user.name || '',
          phone: user.phone || ''
        });
        this.profileForm.markAsPristine();
        this.isUpdating = false;
        this.updateSuccess = true;
        
        // Auto-hide success message after 5 seconds
        setTimeout(() => {
          this.updateSuccess = false;
        }, 5000);
      },
      error: (error: any) => {
        this.isUpdating = false;
        this.errorMessage = error.error?.detail || 'Failed to update profile';
      }
    });
  }

  resetForm(): void {
    this.profileForm.patchValue({
      name: this.currentUser.name || '',
      phone: this.currentUser.phone || ''
    });
    this.profileForm.markAsPristine();
    this.updateSuccess = false;
    this.errorMessage = '';
  }

  getInitials(name: string): string {
    if (!name) return '??';
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  }
}