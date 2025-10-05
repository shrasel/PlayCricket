import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { 
  DeliveryService, 
  InningsService, 
  MatchService, 
  PlayerService 
} from '@core/services';
import {
  BallByBallRequest,
  DismissalType,
  Match,
  Innings,
  InningsScore,
  BatsmanStats,
  BowlerStats
} from '@core/models';

@Component({
  selector: 'app-live-scoring',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="space-y-6">
      <!-- Match Header -->
      @if (match()) {
        <div class="card">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold">{{ match()!.teams?.[0]?.name }} vs {{ match()!.teams?.[1]?.name }}</h1>
              <p class="text-gray-600 dark:text-gray-400">
                {{ match()!.venue?.name }} • {{ match()!.match_type }}
              </p>
            </div>
            <span class="badge badge-live">LIVE</span>
          </div>
        </div>
      }

      <!-- Scorecard -->
      @if (currentScore()) {
        <div class="card">
          <h2 class="text-xl font-bold mb-4">Current Score</h2>
          <div class="score-display">
            {{ currentScore()!.total_runs }}/{{ currentScore()!.total_wickets }}
            <span class="text-2xl ml-2">({{ currentScore()!.total_overs }})</span>
          </div>
          <div class="run-rate mt-2">
            Run Rate: {{ currentScore()!.run_rate.toFixed(2) }}
          </div>
        </div>
      }

      <!-- Current Batsmen -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        @if (batsmanStats()) {
          <div class="card">
            <h3 class="font-semibold mb-3">Striker</h3>
            <div class="text-lg font-bold">{{ batsmanStats()!.runs }}* ({{ batsmanStats()!.balls }})</div>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              SR: {{ batsmanStats()!.strike_rate.toFixed(2) }} | 4s: {{ batsmanStats()!.fours }} | 6s: {{ batsmanStats()!.sixes }}
            </div>
          </div>
        }
        
        @if (bowlerStats()) {
          <div class="card">
            <h3 class="font-semibold mb-3">Bowler</h3>
            <div class="text-lg font-bold">{{ bowlerStats()!.wickets }}/{{ bowlerStats()!.runs }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              Overs: {{ bowlerStats()!.overs }} | Econ: {{ bowlerStats()!.economy.toFixed(2) }}
            </div>
          </div>
        }
      </div>

      <!-- Ball-by-Ball Input Form -->
      <div class="card">
        <h2 class="text-xl font-bold mb-4">Record Delivery</h2>
        
        <form (ngSubmit)="recordDelivery()" class="space-y-4">
          <!-- Over and Ball Number -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">Over Number</label>
              <input type="number" [(ngModel)]="delivery.over_number" name="over_number" 
                     class="input" required min="1">
            </div>
            <div>
              <label class="label">Ball Number</label>
              <input type="number" [(ngModel)]="delivery.ball_number" name="ball_number" 
                     class="input" required min="1" max="6">
            </div>
          </div>

          <!-- Runs Scored -->
          <div>
            <label class="label">Runs Scored</label>
            <div class="grid grid-cols-7 gap-2">
              @for (run of [0, 1, 2, 3, 4, 5, 6]; track run) {
                <button type="button" 
                        (click)="setRuns(run)"
                        [class.bg-primary-600]="delivery.runs_scored === run"
                        [class.text-white]="delivery.runs_scored === run"
                        class="btn btn-secondary">
                  {{ run }}
                </button>
              }
            </div>
          </div>

          <!-- Extras -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">Extras Type</label>
              <select [(ngModel)]="delivery.extras_type" name="extras_type" class="input">
                <option [value]="undefined">None</option>
                <option value="WIDE">Wide</option>
                <option value="NO_BALL">No Ball</option>
                <option value="BYE">Bye</option>
                <option value="LEG_BYE">Leg Bye</option>
              </select>
            </div>
            <div>
              <label class="label">Extra Runs</label>
              <input type="number" [(ngModel)]="delivery.extras_runs" name="extras_runs" 
                     class="input" min="0">
            </div>
          </div>

          <!-- Wicket -->
          <div class="space-y-2">
            <label class="flex items-center space-x-2">
              <input type="checkbox" [(ngModel)]="delivery.is_wicket" name="is_wicket" 
                     class="rounded">
              <span class="label">Wicket</span>
            </label>
            
            @if (delivery.is_wicket) {
              <select [(ngModel)]="delivery.dismissal_type" name="dismissal_type" class="input">
                <option value="BOWLED">Bowled</option>
                <option value="CAUGHT">Caught</option>
                <option value="LBW">LBW</option>
                <option value="RUN_OUT">Run Out</option>
                <option value="STUMPED">Stumped</option>
                <option value="HIT_WICKET">Hit Wicket</option>
              </select>
            }
          </div>

          <!-- Shot & Pitch Coordinates -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">Shot X (0-100)</label>
              <input type="number" [(ngModel)]="delivery.shot_x" name="shot_x" 
                     class="input" min="0" max="100">
            </div>
            <div>
              <label class="label">Shot Y (0-100)</label>
              <input type="number" [(ngModel)]="delivery.shot_y" name="shot_y" 
                     class="input" min="0" max="100">
            </div>
          </div>

          <!-- Commentary -->
          <div>
            <label class="label">Commentary</label>
            <textarea [(ngModel)]="delivery.commentary" name="commentary" 
                      class="input" rows="2" 
                      placeholder="Describe the delivery..."></textarea>
          </div>

          <!-- Submit Button -->
          <button type="submit" class="btn btn-primary w-full">
            Record Delivery
          </button>
        </form>
      </div>

      <!-- Recent Deliveries -->
      @if (recentDeliveries().length > 0) {
        <div class="card">
          <h2 class="text-xl font-bold mb-4">Current Over</h2>
          <div class="flex flex-wrap gap-2">
            @for (del of recentDeliveries(); track $index) {
              <div class="px-3 py-2 rounded-md font-mono" 
                   [class.bg-red-100]="del.is_wicket"
                   [class.bg-green-100]="del.is_boundary && !del.is_wicket"
                   [class.bg-gray-100]="!del.is_wicket && !del.is_boundary">
                {{ formatDelivery(del) }}
              </div>
            }
          </div>
        </div>
      }
    </div>
  `,
  styles: []
})
export class LiveScoringComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private matchService = inject(MatchService);
  private inningsService = inject(InningsService);
  private deliveryService = inject(DeliveryService);

  match = signal<Match | null>(null);
  currentInnings = signal<Innings | null>(null);
  currentScore = signal<InningsScore | null>(null);
  batsmanStats = signal<BatsmanStats | null>(null);
  bowlerStats = signal<BowlerStats | null>(null);
  recentDeliveries = signal<any[]>([]);

  delivery: BallByBallRequest = {
    innings_id: 0,
    over_number: 1,
    ball_number: 1,
    bowler_id: 0,
    batsman_id: 0,
    non_striker_id: 0,
    runs_scored: 0,
    extras_runs: 0,
    is_wicket: false
  };

  ngOnInit() {
    const matchId = this.route.snapshot.paramMap.get('matchId');
    if (matchId) {
      this.loadMatch(matchId);
    }
  }

  loadMatch(matchId: string) {
    this.matchService.getById(matchId).subscribe({
      next: (match) => {
        this.match.set(match);
        // Load current innings
        // this.loadCurrentInnings();
      },
      error: (err) => console.error('Error loading match:', err)
    });
  }

  setRuns(runs: number) {
    this.delivery.runs_scored = runs;
  }

  recordDelivery() {
    this.deliveryService.recordBallByBall(this.delivery).subscribe({
      next: (delivery) => {
        console.log('Delivery recorded:', delivery);
        // Refresh scorecard
        this.refreshScore();
        // Reset form for next delivery
        this.delivery.ball_number++;
        if (this.delivery.ball_number > 6) {
          this.delivery.over_number++;
          this.delivery.ball_number = 1;
        }
        this.delivery.runs_scored = 0;
        this.delivery.extras_runs = 0;
        this.delivery.is_wicket = false;
        this.delivery.commentary = '';
      },
      error: (err) => console.error('Error recording delivery:', err)
    });
  }

  refreshScore() {
    if (this.delivery.innings_id) {
      this.inningsService.getInningsScore(this.delivery.innings_id.toString()).subscribe({
        next: (score) => this.currentScore.set(score),
        error: (err) => console.error('Error loading score:', err)
      });
    }
  }

  formatDelivery(delivery: any): string {
    if (delivery.is_wicket) return 'W';
    if (delivery.is_six) return '6';
    if (delivery.is_boundary) return '4';
    if (delivery.extras_type === 'WIDE') return 'Wd';
    if (delivery.extras_type === 'NO_BALL') return 'NB';
    return delivery.runs_scored.toString();
  }
}
