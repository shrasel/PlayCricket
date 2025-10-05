import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-not-found',
  standalone: true,
  imports: [RouterLink],
  template: `
    <div class="flex flex-col items-center justify-center min-h-[60vh]">
      <h1 class="text-6xl font-bold text-gray-300 mb-4">404</h1>
      <h2 class="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-4">
        Page Not Found
      </h2>
      <p class="text-gray-600 dark:text-gray-400 mb-8">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <a routerLink="/" class="btn btn-primary">
        Go Home
      </a>
    </div>
  `,
  styles: []
})
export class NotFoundComponent {}
