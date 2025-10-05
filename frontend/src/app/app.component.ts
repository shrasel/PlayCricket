import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from '@shared/components/header/header.component';
import { FooterComponent } from '@shared/components/footer/footer.component';
import { LoadingSpinnerComponent } from '@shared/components/loading-spinner/loading-spinner.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, FooterComponent, LoadingSpinnerComponent],
  template: `
    <div class="min-h-screen flex flex-col">
      <app-header></app-header>
      
      <main class="flex-1 container mx-auto px-4 py-8">
        <router-outlet></router-outlet>
      </main>
      
      <app-footer></app-footer>
      
      <app-loading-spinner></app-loading-spinner>
    </div>
  `,
  styles: []
})
export class AppComponent {
  title = 'PlayCricket - Live Cricket Scoring';
}
