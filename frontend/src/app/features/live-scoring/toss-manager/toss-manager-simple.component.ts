import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Match } from '../../../core/models';

@Component({
  selector: 'app-toss-manager',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="max-w-4xl mx-auto">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">Toss Manager</h2>
        
        <div class="space-y-6">
          <!-- Team Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
              Who won the toss?
            </label>
            <div class="grid grid-cols-2 gap-4">
              <button
                (click)="selectTossWinner(getTeamId(0))"
                [class.ring-2]="selectedTeamId === getTeamId(0)"
                [class.ring-indigo-600]="selectedTeamId === getTeamId(0)"
                class="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-indigo-400 transition-all">
                <div class="text-lg font-semibold">{{ getTeamName(0) }}</div>
              </button>
              <button
                (click)="selectTossWinner(getTeamId(1))"
                [class.ring-2]="selectedTeamId === getTeamId(1)"
                [class.ring-indigo-600]="selectedTeamId === getTeamId(1)"
                class="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-indigo-400 transition-all">
                <div class="text-lg font-semibold">{{ getTeamName(1) }}</div>
              </button>
            </div>
          </div>

          <!-- Decision Selection -->
          <div *ngIf="selectedTeamId">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
              Decision
            </label>
            <div class="grid grid-cols-2 gap-4">
              <button
                (click)="selectDecision('BAT')"
                [class.ring-2]="selectedDecision === 'BAT'"
                [class.ring-green-600]="selectedDecision === 'BAT'"
                class="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-green-400 transition-all">
                <div class="text-lg font-semibold">Bat First</div>
              </button>
              <button
                (click)="selectDecision('BOWL')"
                [class.ring-2]="selectedDecision === 'BOWL'"
                [class.ring-orange-600]="selectedDecision === 'BOWL'"
                class="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-orange-400 transition-all">
                <div class="text-lg font-semibold">Bowl First</div>
              </button>
            </div>
          </div>

          <!-- Summary -->
          <div *ngIf="isValid" class="p-4 bg-indigo-50 dark:bg-indigo-900/30 rounded-lg">
            <p class="text-sm text-indigo-700 dark:text-indigo-300">
              <strong>{{ selectedTeamId === getTeamId(0) ? getTeamName(0) : getTeamName(1) }}</strong> won the toss and chose to 
              <strong>{{ selectedDecision === 'BAT' ? 'bat first' : 'bowl first' }}</strong>
            </p>
          </div>

          <!-- Actions -->
          <div class="flex justify-end">
            <button
              (click)="submitToss()"
              [disabled]="!isValid"
              [class.opacity-50]="!isValid"
              [class.cursor-not-allowed]="!isValid"
              class="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:hover:bg-indigo-600 transition-colors">
              Continue to Team Lineup
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class TossManagerComponent {
  @Input() match!: Match;
  @Output() tossComplete = new EventEmitter<{ winnerId: number; decision: 'BAT' | 'BOWL' }>();

  selectedTeamId?: number;
  selectedDecision?: 'BAT' | 'BOWL';

  selectTossWinner(teamId: number): void {
    this.selectedTeamId = teamId;
  }

  selectDecision(decision: 'BAT' | 'BOWL'): void {
    this.selectedDecision = decision;
  }

  submitToss(): void {
    if (this.selectedTeamId && this.selectedDecision) {
      this.tossComplete.emit({
        winnerId: this.selectedTeamId,
        decision: this.selectedDecision
      });
    }
  }

  get isValid(): boolean {
    return !!this.selectedTeamId && !!this.selectedDecision;
  }

  getTeamName(index: number): string {
    return this.match.teams?.[index]?.name || `Team ${index + 1}`;
  }

  getTeamId(index: number): number {
    const publicId = this.match.teams?.[index]?.public_id;
    return publicId ? parseInt(publicId) : 0;
  }
}
