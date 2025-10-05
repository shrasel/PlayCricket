import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

interface Device {
  id: number;
  device_name: string;
  ip_address: string;
  created_at: string;
  last_used_at: string;
  is_current: boolean;
}

@Component({
  selector: 'app-devices',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="mb-8">
          <a routerLink="/profile" 
             class="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 mb-4">
            <svg class="mr-1 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Profile
          </a>
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white">
                Active Sessions
              </h1>
              <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Manage devices and sessions where you're currently logged in
              </p>
            </div>
            <button
              (click)="logoutAllDevices()"
              [disabled]="isLoading || devices.length <= 1"
              class="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Logout All Devices
            </button>
          </div>
        </div>

        <!-- Success Message -->
        <div *ngIf="successMessage" class="mb-4 rounded-md bg-green-50 dark:bg-green-900/20 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium text-green-800 dark:text-green-200">
                {{ successMessage }}
              </p>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div *ngIf="errorMessage" class="mb-4 rounded-md bg-red-50 dark:bg-red-900/20 p-4">
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

        <!-- Loading State -->
        <div *ngIf="isLoading && devices.length === 0" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div class="animate-pulse space-y-4">
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
          </div>
        </div>

        <!-- Devices List -->
        <div *ngIf="devices.length > 0" class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
          <ul class="divide-y divide-gray-200 dark:divide-gray-700">
            <li *ngFor="let device of devices" class="px-6 py-5">
              <div class="flex items-center justify-between">
                <div class="flex items-center flex-1 min-w-0">
                  <!-- Device Icon -->
                  <div class="flex-shrink-0">
                    <div class="h-12 w-12 rounded-full flex items-center justify-center"
                         [ngClass]="{
                           'bg-green-100 dark:bg-green-900/20': device.is_current,
                           'bg-gray-100 dark:bg-gray-700': !device.is_current
                         }">
                      <svg class="h-6 w-6" 
                           [ngClass]="{
                             'text-green-600 dark:text-green-400': device.is_current,
                             'text-gray-600 dark:text-gray-400': !device.is_current
                           }"
                           fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              [attr.d]="getDeviceIcon(device.device_name)" />
                      </svg>
                    </div>
                  </div>

                  <!-- Device Info -->
                  <div class="ml-4 flex-1 min-w-0">
                    <div class="flex items-center">
                      <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {{ device.device_name }}
                      </p>
                      <span *ngIf="device.is_current" 
                            class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                        Current Device
                      </span>
                    </div>
                    <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                      IP Address: {{ device.ip_address }}
                    </p>
                    <p class="mt-1 text-xs text-gray-500 dark:text-gray-500">
                      Last active: {{ device.last_used_at | date:'medium' }}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-500">
                      Logged in: {{ device.created_at | date:'medium' }}
                    </p>
                  </div>
                </div>

                <!-- Actions -->
                <div class="ml-4 flex-shrink-0">
                  <button
                    *ngIf="!device.is_current"
                    (click)="revokeDevice(device.id)"
                    [disabled]="revokingDeviceId === device.id"
                    class="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                  >
                    <svg *ngIf="revokingDeviceId !== device.id" class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    <svg *ngIf="revokingDeviceId === device.id" class="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ revokingDeviceId === device.id ? 'Revoking...' : 'Revoke' }}
                  </button>
                  <span *ngIf="device.is_current" 
                        class="inline-flex items-center px-3 py-2 text-sm text-gray-500 dark:text-gray-400">
                    —
                  </span>
                </div>
              </div>
            </li>
          </ul>
        </div>

        <!-- Empty State -->
        <div *ngIf="!isLoading && devices.length === 0" class="bg-white dark:bg-gray-800 shadow rounded-lg p-12 text-center">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No active sessions</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            No other devices are currently logged in to your account.
          </p>
        </div>

        <!-- Info Card -->
        <div class="mt-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-blue-700 dark:text-blue-300">
                <strong>Security Tip:</strong> If you see any unfamiliar devices or locations, revoke them immediately and change your password.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class DevicesComponent implements OnInit {
  devices: Device[] = [];
  isLoading = false;
  revokingDeviceId: number | null = null;
  successMessage = '';
  errorMessage = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadDevices();
  }

  loadDevices(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.authService.getActiveDevices().subscribe({
      next: (devices: any) => {
        this.devices = devices;
        this.isLoading = false;
      },
      error: (error: any) => {
        this.errorMessage = error.message || 'Failed to load devices';
        this.isLoading = false;
      }
    });
  }

  revokeDevice(deviceId: number): void {
    if (!confirm('Are you sure you want to revoke this session? You will be logged out on that device.')) {
      return;
    }

    this.revokingDeviceId = deviceId;
    this.errorMessage = '';
    this.successMessage = '';

    this.authService.revokeDevice(deviceId).subscribe({
      next: () => {
        this.revokingDeviceId = null;
        this.successMessage = 'Session revoked successfully';
        // Remove the device from the list
        this.devices = this.devices.filter(d => d.id !== deviceId);
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error: any) => {
        this.revokingDeviceId = null;
        this.errorMessage = error.message || 'Failed to revoke session';
      }
    });
  }

  logoutAllDevices(): void {
    if (!confirm('Are you sure you want to logout from all devices? You will need to sign in again on all your devices including this one.')) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.logoutAllDevices().subscribe({
      next: () => {
        // This will log out the current device too, redirecting to login
        alert('Logged out from all devices successfully');
        this.router.navigate(['/login']);
      },
      error: (error: any) => {
        this.isLoading = false;
        this.errorMessage = error.message || 'Failed to logout all devices';
      }
    });
  }

  getDeviceIcon(deviceName: string): string {
    const name = deviceName.toLowerCase();
    
    // Mobile devices
    if (name.includes('iphone') || name.includes('ipad') || name.includes('android') || name.includes('mobile')) {
      return 'M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z';
    }
    
    // Desktop/Laptop
    return 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z';
  }
}
