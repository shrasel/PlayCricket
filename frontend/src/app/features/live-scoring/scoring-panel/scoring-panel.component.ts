import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Match, Innings } from '../../../core/models';

interface MatchSetup {
  tossWinnerId?: number;
  tossDecision?: 'BAT' | 'BOWL';
  team1Players: any[];
  team2Players: any[];
  team1Lineup: number[];
  team2Lineup: number[];
  battingTeamId?: number;
  bowlingTeamId?: number;
}

@Component({
  selector: 'app-scoring-panel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
      <div class="text-center">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Scoring Panel</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          This is where the live scoring interface will be displayed.
        </p>
        
        @if (match) {
          <div class="bg-indigo-50 dark:bg-indigo-900/30 rounded-lg p-6 mb-6">
            <h3 class="font-semibold text-indigo-900 dark:text-indigo-100 mb-2">Match Information</h3>
            <p class="text-sm text-indigo-700 dark:text-indigo-300">
              {{ match.teams?.[0]?.name || 'Team 1' }} vs {{ match.teams?.[1]?.name || 'Team 2' }}
            </p>
            @if (innings) {
              <p class="text-xs text-indigo-600 dark:text-indigo-400 mt-2">
                Innings {{ innings.innings_number }} - {{ innings.innings_type }}
              </p>
            }
          </div>
        }
        
        <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <p class="text-sm text-yellow-800 dark:text-yellow-300">
            <strong>Coming Soon:</strong> Full ball-by-ball scoring interface with delivery entry, 
            quick actions, partnership tracker, and real-time scorecard updates.
          </p>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class ScoringPanelComponent {
  @Input() match!: Match;
  @Input() innings?: Innings;
  @Input() matchSetup!: MatchSetup;
}
