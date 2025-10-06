import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';

import { MatchService } from '../../../core/services/match.service';
import { InningsService } from '../../../core/services/innings.service';
import { TeamService } from '../../../core/services/team.service';
import { PlayerService } from '../../../core/services/player.service';

import { Match, Team, Player, Innings, InningsType, MatchStatus } from '../../../core/models';

// import { TossManagerComponent } from '../toss-manager/toss-manager.component';
// import { TeamLineupComponent } from '../team-lineup/team-lineup.component';
import { ScoringPanelComponent } from '../scoring-panel/scoring-panel.component';

type ScoringStep = 'toss' | 'lineup' | 'scoring';

interface MatchSetup {
  tossWinnerId?: number;
  tossDecision?: 'BAT' | 'BOWL';
  team1Players: Player[];
  team2Players: Player[];
  team1Lineup: number[];
  team2Lineup: number[];
  battingTeamId?: number;
  bowlingTeamId?: number;
}

@Component({
  selector: 'app-live-scoring-main',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule,
    // TossManagerComponent,
    // TeamLineupComponent,
    ScoringPanelComponent
  ],
  templateUrl: './live-scoring-main.component.html',
  styleUrl: './live-scoring-main.component.scss'
})
export class LiveScoringMainComponent implements OnInit {
  matchId: string = '';
  match: Match | null = null;
  currentInnings: Innings | undefined = undefined;
  
  loading = true;
  error: string | null = null;
  
  currentStep: ScoringStep = 'toss';
  matchSetup: MatchSetup = {
    team1Players: [],
    team2Players: [],
    team1Lineup: [],
    team2Lineup: []
  };

  teams: Team[] = [];
  allPlayers: Player[] = [];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private matchService: MatchService,
    private inningsService: InningsService,
    private teamService: TeamService,
    private playerService: PlayerService
  ) {}

  ngOnInit(): void {
    this.matchId = this.route.snapshot.paramMap.get('matchId') || '';
    
    if (!this.matchId) {
      this.router.navigate(['/live-scoring']);
      return;
    }

    this.loadMatch();
  }

  loadMatch(): void {
    this.loading = true;
    this.error = null;

    this.matchService.getById(this.matchId).subscribe({
      next: (match) => {
        this.match = match;
        
        // Check if match is ready for scoring
        if (match.status === 'COMPLETED' || match.status === 'ABANDONED' || match.status === 'CANCELLED') {
          this.error = 'This match is already completed or cancelled';
          this.loading = false;
          return;
        }

        // Load teams and players
        this.loadTeamsAndPlayers();
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to load match';
        this.loading = false;
      }
    });
  }

  loadTeamsAndPlayers(): void {
    if (!this.match?.teams || this.match.teams.length < 2) {
      this.error = 'Match must have 2 teams';
      this.loading = false;
      return;
    }

    // Load all players
    this.playerService.getAll({ limit: 1000 }).subscribe({
      next: (response) => {
        this.allPlayers = response.items || [];
        
        // Check if innings already exists (match in progress)
        this.checkExistingInnings();
      },
      error: (err) => {
        this.error = 'Failed to load players';
        this.loading = false;
      }
    });
  }

  checkExistingInnings(): void {
    if (!this.match) return;

    this.inningsService.getAll({ match_id: this.match.id, limit: 10 }).subscribe({
      next: (response) => {
        const innings = response.items || [];
        
        if (innings.length > 0) {
          // Match already has innings, go directly to scoring
          this.currentInnings = innings[innings.length - 1]; // Get latest innings
          this.currentStep = 'scoring';
        } else {
          // New match, start with toss
          this.currentStep = 'toss';
        }
        
        this.loading = false;
      },
      error: (err) => {
        console.error('Error checking innings:', err);
        this.loading = false;
      }
    });
  }

  onTossComplete(tossData: { winnerId: number; decision: 'BAT' | 'BOWL' }): void {
    this.matchSetup.tossWinnerId = tossData.winnerId;
    this.matchSetup.tossDecision = tossData.decision;
    
    // Determine batting and bowling teams
    if (tossData.decision === 'BAT') {
      this.matchSetup.battingTeamId = tossData.winnerId;
      this.matchSetup.bowlingTeamId = this.getOtherTeamId(tossData.winnerId);
    } else {
      this.matchSetup.bowlingTeamId = tossData.winnerId;
      this.matchSetup.battingTeamId = this.getOtherTeamId(tossData.winnerId);
    }

    // Move to lineup selection
    this.currentStep = 'lineup';
  }

  onLineupComplete(lineupData: any): void {
    this.matchSetup.team1Lineup = lineupData.team1Lineup;
    this.matchSetup.team2Lineup = lineupData.team2Lineup;
    
    // Create first innings
    this.createFirstInnings();
  }

  createFirstInnings(): void {
    if (!this.match || !this.matchSetup.battingTeamId || !this.matchSetup.bowlingTeamId) {
      this.error = 'Invalid match setup';
      return;
    }

    this.loading = true;

    const inningsData = {
      match_id: this.match.id,
      innings_number: 1,
      innings_type: InningsType.FIRST,
      batting_team_id: this.matchSetup.battingTeamId,
      bowling_team_id: this.matchSetup.bowlingTeamId
    };

    this.inningsService.create(inningsData).subscribe({
      next: (innings) => {
        this.currentInnings = innings;
        
        // Update match status to LIVE
        this.updateMatchStatus(MatchStatus.LIVE);
        
        // Move to scoring
        this.currentStep = 'scoring';
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to create innings';
        this.loading = false;
      }
    });
  }

  updateMatchStatus(status: MatchStatus): void {
    if (!this.match) return;

    this.matchService.update(this.match.public_id, { status }).subscribe({
      next: (updatedMatch) => {
        this.match = updatedMatch;
      },
      error: (err) => {
        console.error('Failed to update match status:', err);
      }
    });
  }

  getOtherTeamId(teamId: number): number {
    if (!this.match?.teams) return 0;
    
    // TeamSummary uses public_id (string), but we need to match by actual team id
    // This is a workaround - in production, you'd need team id lookup
    const teams = this.match.teams;
    return teams.length === 2 && teams[0].public_id !== teamId.toString() 
      ? parseInt(teams[1].public_id) || 0
      : parseInt(teams[0].public_id) || 0;
  }

  getTeamName(teamId: number | undefined): string {
    if (!teamId || !this.match?.teams) return 'Unknown';
    
    const team = this.match.teams.find(t => parseInt(t.public_id) === teamId);
    return team?.name || 'Unknown';
  }

  goBack(): void {
    if (this.currentStep === 'lineup') {
      this.currentStep = 'toss';
    } else if (this.currentStep === 'toss') {
      this.router.navigate(['/live-scoring']);
    }
  }
}
