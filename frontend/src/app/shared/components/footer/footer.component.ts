import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  template: `
    <footer class="bg-gray-800 text-white mt-auto">
      <div class="container mx-auto px-4 py-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- About Section -->
          <div>
            <h3 class="text-lg font-bold mb-4">PlayCricket</h3>
            <p class="text-gray-400">
              Live cricket scoring platform with ball-by-ball updates, statistics, and analytics.
            </p>
          </div>

          <!-- Quick Links -->
          <div>
            <h3 class="text-lg font-bold mb-4">Quick Links</h3>
            <ul class="space-y-2 text-gray-400">
              <li><a href="/matches" class="hover:text-white">Matches</a></li>
              <li><a href="/live-scoring" class="hover:text-white">Live Scoring</a></li>
              <li><a href="/teams" class="hover:text-white">Teams</a></li>
              <li><a href="/players" class="hover:text-white">Players</a></li>
              <li><a href="/statistics" class="hover:text-white">Statistics</a></li>
            </ul>
          </div>

          <!-- Contact -->
          <div>
            <h3 class="text-lg font-bold mb-4">Connect</h3>
            <p class="text-gray-400 mb-2">Built with ❤️ for cricket fans</p>
            <div class="flex space-x-4">
              <a href="#" class="text-gray-400 hover:text-white">📧</a>
              <a href="#" class="text-gray-400 hover:text-white">🐦</a>
              <a href="#" class="text-gray-400 hover:text-white">📘</a>
            </div>
          </div>
        </div>

        <!-- Copyright -->
        <div class="border-t border-gray-700 mt-8 pt-6 text-center text-gray-400">
          <p>&copy; {{ currentYear }} PlayCricket. All rights reserved.</p>
        </div>
      </div>
    </footer>
  `,
  styles: []
})
export class FooterComponent {
  currentYear = new Date().getFullYear();
}
