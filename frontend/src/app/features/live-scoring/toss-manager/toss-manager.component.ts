import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Match } from '../../../core/models';

@Component({
  selector: 'app-toss-manager',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './toss-manager.component.html',
  styleUrls: ['./toss-manager.component.scss']
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
