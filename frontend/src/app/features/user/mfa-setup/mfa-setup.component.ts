import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-mfa-setup',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-2xl mx-auto">
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
            Two-Factor Authentication
          </h1>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Add an extra layer of security to your account
          </p>
        </div>

        <!-- MFA Status Card -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg mb-6">
          <div class="px-6 py-5">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                  MFA Status
                </h3>
                <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  {{ mfaEnabled ? 'Two-factor authentication is enabled' : 'Two-factor authentication is disabled' }}
                </p>
              </div>
              <span [ngClass]="{
                'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400': mfaEnabled,
                'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': !mfaEnabled
              }" class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium">
                {{ mfaEnabled ? 'Enabled' : 'Disabled' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Setup MFA (if not enabled) -->
        <div *ngIf="!mfaEnabled" class="bg-white dark:bg-gray-800 shadow rounded-lg">
          <!-- Step 1: Get QR Code -->
          <div *ngIf="!qrCodeUrl" class="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Step 1: Set Up Authenticator
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Install an authenticator app like Google Authenticator, Authy, or Microsoft Authenticator on your phone.
            </p>
            <button
              (click)="setupMFA()"
              [disabled]="isLoading"
              class="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {{ isLoading ? 'Generating...' : 'Generate QR Code' }}
            </button>
          </div>

          <!-- Step 2: Scan QR Code -->
          <div *ngIf="qrCodeUrl && !mfaEnabled" class="px-6 py-5">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Step 2: Scan QR Code
            </h3>
            
            <!-- QR Code Display -->
            <div class="flex flex-col items-center mb-6">
              <img [src]="qrCodeUrl" alt="QR Code" class="w-64 h-64 border-2 border-gray-200 dark:border-gray-700 rounded-lg" />
              <p class="mt-4 text-sm text-gray-600 dark:text-gray-400 text-center">
                Scan this QR code with your authenticator app
              </p>
              <p class="mt-2 text-xs text-gray-500 dark:text-gray-500">
                Or manually enter the secret: <code class="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">{{ mfaSecret }}</code>
              </p>
            </div>

            <!-- Backup Codes -->
            <div *ngIf="backupCodes && backupCodes.length > 0" class="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <h4 class="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-2">
                ⚠️ Save Your Backup Codes
              </h4>
              <p class="text-xs text-yellow-700 dark:text-yellow-300 mb-3">
                Store these backup codes in a safe place. You can use them to access your account if you lose your authenticator device.
              </p>
              <div class="grid grid-cols-2 gap-2 mb-3">
                <code *ngFor="let code of backupCodes" 
                      class="bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-3 py-2 rounded text-sm font-mono border border-yellow-200 dark:border-yellow-800">
                  {{ code }}
                </code>
              </div>
              <button
                (click)="downloadBackupCodes()"
                class="text-xs font-medium text-yellow-800 dark:text-yellow-200 hover:text-yellow-900 dark:hover:text-yellow-100 underline"
              >
                Download backup codes
              </button>
            </div>

            <!-- Step 3: Verify -->
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Step 3: Verify Code
            </h3>
            
            <!-- Error Message -->
            <div *ngIf="errorMessage" class="mb-4 rounded-md bg-red-50 dark:bg-red-900/20 p-4">
              <p class="text-sm font-medium text-red-800 dark:text-red-200">
                {{ errorMessage }}
              </p>
            </div>

            <form [formGroup]="verifyForm" (ngSubmit)="enableMFA()" class="space-y-4">
              <div>
                <label for="code" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Enter the 6-digit code from your authenticator app
                </label>
                <input
                  id="code"
                  formControlName="otp_code"
                  type="text"
                  maxlength="6"
                  class="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  placeholder="000000"
                />
              </div>

              <div class="flex justify-end space-x-3">
                <button
                  type="button"
                  (click)="cancelSetup()"
                  class="px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  [disabled]="verifyForm.invalid || isEnabling"
                  class="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {{ isEnabling ? 'Verifying...' : 'Enable MFA' }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Disable MFA (if enabled) -->
        <div *ngIf="mfaEnabled" class="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div class="px-6 py-5">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Disable Two-Factor Authentication
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
              Disabling MFA will make your account less secure. You'll need to enter your password to confirm.
            </p>

            <!-- Error Message -->
            <div *ngIf="errorMessage" class="mb-4 rounded-md bg-red-50 dark:bg-red-900/20 p-4">
              <p class="text-sm font-medium text-red-800 dark:text-red-200">
                {{ errorMessage }}
              </p>
            </div>

            <form [formGroup]="disableForm" (ngSubmit)="disableMFA()" class="space-y-4">
              <div>
                <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Current Password
                </label>
                <input
                  id="password"
                  formControlName="password"
                  type="password"
                  class="appearance-none block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  placeholder="Enter your password"
                />
              </div>

              <div class="flex justify-end space-x-3">
                <button
                  type="button"
                  (click)="goBack()"
                  class="px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  [disabled]="disableForm.invalid || isDisabling"
                  class="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                >
                  {{ isDisabling ? 'Disabling...' : 'Disable MFA' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  `
})
export class MfaSetupComponent implements OnInit {
  mfaEnabled = false;
  qrCodeUrl: SafeUrl | null = null;
  mfaSecret = '';
  backupCodes: string[] = [];
  
  verifyForm: FormGroup;
  disableForm: FormGroup;
  
  isLoading = false;
  isEnabling = false;
  isDisabling = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private sanitizer: DomSanitizer
  ) {
    this.verifyForm = this.fb.group({
      otp_code: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(6)]]
    });

    this.disableForm = this.fb.group({
      password: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    // Check if MFA is already enabled
    this.authService.currentUser$.subscribe(user => {
      if (user) {
        this.mfaEnabled = user.mfa_enabled || false;
      }
    });
  }

  setupMFA(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.authService.setupMFA().subscribe({
      next: (response: any) => {
        this.qrCodeUrl = this.sanitizer.bypassSecurityTrustUrl(response.qr_code);
        this.mfaSecret = response.secret;
        this.backupCodes = response.backup_codes || [];
        this.isLoading = false;
      },
      error: (error: any) => {
        this.errorMessage = error.message || 'Failed to generate QR code';
        this.isLoading = false;
      }
    });
  }

  enableMFA(): void {
    if (this.verifyForm.invalid) {
      return;
    }

    this.isEnabling = true;
    this.errorMessage = '';

    this.authService.enableMFA(this.mfaSecret, this.verifyForm.value.otp_code, this.backupCodes).subscribe({
      next: () => {
        this.isEnabling = false;
        this.mfaEnabled = true;
        alert('MFA enabled successfully!');
        this.router.navigate(['/profile']);
      },
      error: (error: any) => {
        this.isEnabling = false;
        this.errorMessage = error.message || 'Invalid verification code';
      }
    });
  }

  disableMFA(): void {
    if (this.disableForm.invalid) {
      return;
    }

    this.isDisabling = true;
    this.errorMessage = '';

    this.authService.disableMFA(this.disableForm.value.password).subscribe({
      next: () => {
        this.isDisabling = false;
        this.mfaEnabled = false;
        alert('MFA disabled successfully');
        this.router.navigate(['/profile']);
      },
      error: (error: any) => {
        this.isDisabling = false;
        this.errorMessage = error.message || 'Failed to disable MFA';
      }
    });
  }

  cancelSetup(): void {
    this.qrCodeUrl = null;
    this.backupCodes = [];
    this.verifyForm.reset();
  }

  downloadBackupCodes(): void {
    const content = this.backupCodes.join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'playcricket-backup-codes.txt';
    a.click();
    window.URL.revokeObjectURL(url);
  }

  goBack(): void {
    this.router.navigate(['/profile']);
  }
}
