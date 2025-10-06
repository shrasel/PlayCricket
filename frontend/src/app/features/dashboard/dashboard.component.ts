import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatchService } from '@core/services';
import { Match, MatchStatus } from '@core/models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="space-y-8">
      <!-- Hero Section -->
      <div class="card cricket-field text-white">
        <h1 class="text-4xl font-bold mb-2">Welcome to PlayCricket</h1>
        <p class="text-lg opacity-90">Live Cricket Scoring & Statistics Platform</p>
      </div>

      <!-- Live Matches -->
      <section>
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
            Live Matches 🔴
          </h2>
          <a routerLink="/matches" class="text-primary-600 hover:text-primary-700">
            View All →
          </a>
        </div>
        
        @if (liveMatches.length > 0) {
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            @for (match of liveMatches; track match.public_id) {
              <div class="card hover:shadow-lg transition-shadow cursor-pointer" 
                   [routerLink]="['/matches', match.public_id]">
                <div class="flex items-center justify-between mb-2">
                  <span class="badge badge-live">LIVE</span>
                  <span class="text-sm text-gray-500">{{ match.match_type }}</span>
                </div>
                <div class="space-y-2">
                  @for (team of match.teams; track team.public_id) {
                    <div class="flex items-center justify-between">
                      <span class="font-semibold">{{ team.short_name }}</span>
                      <span class="text-lg">150/3</span>
                    </div>
                  }
                </div>
                <div class="mt-3 text-sm text-gray-600 dark:text-gray-400">
                  📍 {{ match.venue?.name }}
                </div>
              </div>
            }
          </div>
        } @else {
          <div class="card text-center text-gray-500">
            <p>No live matches at the moment</p>
            <a routerLink="/live-scoring" class="btn btn-primary mt-4 inline-block">
              Start Live Scoring
            </a>
          </div>
        }
      </section>

      <!-- Upcoming Matches -->
      <section>
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
            Upcoming Matches
          </h2>
        </div>
        
        @if (upcomingMatches.length > 0) {
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            @for (match of upcomingMatches; track match.public_id) {
              <div class="card hover:shadow-lg transition-shadow cursor-pointer"
                   [routerLink]="['/matches', match.public_id]">
                <div class="flex items-center justify-between mb-2">
                  <span class="badge badge-upcoming">SCHEDULED</span>
                  <span class="text-sm text-gray-500">{{ match.match_type }}</span>
                </div>
                <div class="space-y-1">
                  @for (team of match.teams; track team.public_id) {
                    <div class="font-semibold">{{ team.name }}</div>
                  }
                </div>
                <div class="mt-3 text-sm text-gray-600 dark:text-gray-400">
                  @if (match.scheduled_start) {
                    🕐 {{ formatDate(match.scheduled_start) }}<br>
                  }
                  📍 {{ match.venue?.name }}
                </div>
              </div>
            }
          </div>
        } @else {
          <div class="card text-center text-gray-500">
            <p>No upcoming matches scheduled</p>
          </div>
        }
      </section>

      <!-- Quick Actions -->
      <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <a routerLink="/matches/create" class="card hover:shadow-lg transition-shadow cursor-pointer text-center">
          <div class="text-4xl mb-2">➕</div>
          <h3 class="font-semibold">Create Match</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">Schedule a new match</p>
        </a>
        
        <a routerLink="/teams" class="card hover:shadow-lg transition-shadow cursor-pointer text-center">
          <div class="text-4xl mb-2">👥</div>
          <h3 class="font-semibold">Manage Teams</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">View and edit teams</p>
        </a>
        
        <a routerLink="/players" class="card hover:shadow-lg transition-shadow cursor-pointer text-center">
          <div class="text-4xl mb-2">🏏</div>
          <h3 class="font-semibold">Manage Players</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">View player profiles</p>
        </a>
        
        <a routerLink="/statistics" class="card hover:shadow-lg transition-shadow cursor-pointer text-center">
          <div class="text-4xl mb-2">📊</div>
          <h3 class="font-semibold">Statistics</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">View detailed stats</p>
        </a>
      </section>

      <!-- Recent Results -->
      <section>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Recent Results
        </h2>
        
        @if (completedMatches.length > 0) {
          <div class="space-y-3">
            @for (match of completedMatches; track match.public_id) {
              <div class="card hover:shadow-lg transition-shadow cursor-pointer"
                   [routerLink]="['/matches', match.public_id]">
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <span class="badge badge-completed">COMPLETED</span>
                    <div class="mt-2 space-y-1">
                      @for (team of match.teams; track team.public_id) {
                        <div class="flex items-center justify-between">
                          <span [class.font-bold]="match.winning_team_id === team.public_id">
                            {{ team.name }}
                          </span>
                          <span>150/8 (20)</span>
                        </div>
                      }
                    </div>
                    @if (match.result_margin) {
                      <p class="mt-2 text-sm text-green-600 dark:text-green-400 font-semibold">
                        {{ match.result_margin }}
                      </p>
                    }
                  </div>
                </div>
              </div>
            }
          </div>
        } @else {
          <div class="card text-center text-gray-500">
            <p>No completed matches yet</p>
          </div>
        }
      </section>
    </div>
  `,
  styles: []
})
export class DashboardComponent implements OnInit {
  private matchService = inject(MatchService);

  liveMatches: Match[] = [];
  upcomingMatches: Match[] = [];
  completedMatches: Match[] = [];
  loading = true;
  error: string | null = null;

  ngOnInit() {
    this.loadMatches();
  }

  async loadMatches() {
    try {
      // Load live matches
      this.matchService.getLiveMatches({ page_size: 6 }).subscribe({
        next: (response) => {
          this.liveMatches = response.items;
        },
        error: (err) => console.error('Error loading live matches:', err)
      });

      // Load upcoming matches
      this.matchService.filterByStatus(MatchStatus.SCHEDULED, { page_size: 4 }).subscribe({
        next: (response) => {
          this.upcomingMatches = response.items;
        },
        error: (err) => console.error('Error loading upcoming matches:', err)
      });

      // Load completed matches
      this.matchService.filterByStatus(MatchStatus.COMPLETED, { page_size: 3 }).subscribe({
        next: (response) => {
          this.completedMatches = response.items;
          this.loading = false;
        },
        error: (err) => {
          console.error('Error loading completed matches:', err);
          this.loading = false;
        }
      });
    } catch (err) {
      this.error = 'Failed to load matches';
      this.loading = false;
    }
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}
