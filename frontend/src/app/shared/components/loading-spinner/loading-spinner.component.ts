import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoadingService } from '@core/services/loading.service';

@Component({
  selector: 'app-loading-spinner',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (loadingService.isLoading()) {
      <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 flex flex-col items-center">
          <div class="loading-spinner"></div>
          <p class="mt-4 text-gray-700 dark:text-gray-300">Loading...</p>
        </div>
      </div>
    }
  `,
  styles: []
})
export class LoadingSpinnerComponent {
  loadingService = inject(LoadingService);
}
