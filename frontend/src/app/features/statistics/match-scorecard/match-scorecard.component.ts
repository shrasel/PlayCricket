import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { forkJoin } from 'rxjs';

import { MatchService } from '../../../core/services/match.service';
import { InningsService } from '../../../core/services/innings.service';
import { DeliveryService } from '../../../core/services/delivery.service';
import { TeamService } from '../../../core/services/team.service';
import { PlayerService } from '../../../core/services/player.service';

import {
  Match,
  Innings,
  InningsScore,
  Partnership,
  Scorecard,
  BattingPerformance,
  BowlingPerformance,
  Delivery,
  TeamSummary,
  PlayerSummary
} from '../../../core/models';

interface FallOfWicket {
  wicketNumber: number;
  runs: number;
  overs: number;
  playerName: string;
  dismissal: string;
}

interface PartnershipData {
  batsman1: string;
  batsman2: string;
  runs: number;
  balls: number;
  batsman1Runs: number;
  batsman2Runs: number;
}

interface RunRateData {
  over: number;
  runs: number;
  cumulative: number;
}

@Component({
  selector: 'app-match-scorecard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './match-scorecard.component.html',
  styleUrl: './match-scorecard.component.scss'
})
export class MatchScorecardComponent implements OnInit {
  matchId: string = '';
  loading = true;
  error: string | null = null;

  match: Match | null = null;
  innings: Innings[] = [];
  selectedInnings: number = 0;
  
  // Scorecard data
  battingPerformances: BattingPerformance[] = [];
  bowlingPerformances: BowlingPerformance[] = [];
  inningsScore: InningsScore | null = null;
  
  // Advanced stats
  fallOfWickets: FallOfWicket[] = [];
  partnerships: PartnershipData[] = [];
  runRateData: RunRateData[] = [];
  
  // Teams cache
  teamsMap = new Map<string, TeamSummary>();
  playersMap = new Map<string, PlayerSummary>();

  constructor(
    private route: ActivatedRoute,
    private matchService: MatchService,
    private inningsService: InningsService,
    private deliveryService: DeliveryService,
    private teamService: TeamService,
    private playerService: PlayerService
  ) {}

  ngOnInit(): void {
    this.matchId = this.route.snapshot.paramMap.get('id') || '';
    if (this.matchId) {
      this.loadMatchData();
    } else {
      this.error = 'Invalid match ID';
      this.loading = false;
    }
  }

  loadMatchData(): void {
    this.loading = true;
    this.error = null;

    forkJoin({
      match: this.matchService.getById(this.matchId),
      innings: this.inningsService.getAll({ match_id: this.matchId, limit: 10 }),
      teams: this.teamService.getAll({ limit: 100 }),
      players: this.playerService.getAll({ limit: 1000 })
    }).subscribe({
      next: (data) => {
        this.match = data.match;
        this.innings = data.innings.items || [];
        
        // Cache teams and players
        data.teams.items?.forEach((team: any) => {
          this.teamsMap.set(team.public_id, team);
        });
        
        data.players.items?.forEach((player: any) => {
          this.playersMap.set(player.public_id, player);
        });

        if (this.innings.length > 0) {
          this.loadInningsDetails(0);
        } else {
          this.loading = false;
        }
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to load match data';
        this.loading = false;
      }
    });
  }

  loadInningsDetails(index: number): void {
    if (index < 0 || index >= this.innings.length) return;
    
    this.selectedInnings = index;
    const innings = this.innings[index];
    this.loading = true;

    forkJoin({
      score: this.inningsService.getInningsScore(innings.public_id),
      deliveries: this.deliveryService.getAll({ innings_id: innings.id, limit: 1000 })
    }).subscribe({
      next: (data) => {
        this.inningsScore = data.score;
        const deliveries = data.deliveries.items || [];
        
        this.processBattingPerformances(deliveries);
        this.processBowlingPerformances(deliveries);
        this.processFallOfWickets(deliveries);
        this.processPartnerships(deliveries);
        this.processRunRateData(deliveries);
        
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to load innings details';
        this.loading = false;
      }
    });
  }

  processBattingPerformances(deliveries: any[]): void {
    const batsmanStats = new Map<number, any>();
    
    deliveries.forEach((delivery: any) => {
      if (!batsmanStats.has(delivery.batsman_id)) {
        batsmanStats.set(delivery.batsman_id, {
          player_id: delivery.batsman_id,
          runs: 0,
          balls: 0,
          fours: 0,
          sixes: 0,
          dismissal: null
        });
      }
      
      const stats = batsmanStats.get(delivery.batsman_id);
      if (delivery.is_legal_delivery) {
        stats.balls++;
      }
      stats.runs += delivery.runs_scored;
      if (delivery.is_boundary && !delivery.is_six) stats.fours++;
      if (delivery.is_six) stats.sixes++;
      
      if (delivery.is_wicket && delivery.batsman_id) {
        stats.dismissal = this.formatDismissal(delivery);
      }
    });

    this.battingPerformances = Array.from(batsmanStats.values()).map(stats => ({
      player: this.playersMap.get(stats.player_id.toString()) || { 
        public_id: stats.player_id.toString(), 
        full_name: 'Unknown Player' 
      } as PlayerSummary,
      runs: stats.runs,
      balls: stats.balls,
      fours: stats.fours,
      sixes: stats.sixes,
      strike_rate: stats.balls > 0 ? (stats.runs / stats.balls) * 100 : 0,
      dismissal: stats.dismissal
    })).sort((a, b) => b.runs - a.runs);
  }

  processBowlingPerformances(deliveries: any[]): void {
    const bowlerStats = new Map<number, any>();
    
    deliveries.forEach((delivery: any) => {
      if (!bowlerStats.has(delivery.bowler_id)) {
        bowlerStats.set(delivery.bowler_id, {
          player_id: delivery.bowler_id,
          balls: 0,
          maidens: 0,
          runs: 0,
          wickets: 0,
          extras: 0
        });
      }
      
      const stats = bowlerStats.get(delivery.bowler_id);
      if (delivery.is_legal_delivery) {
        stats.balls++;
      }
      stats.runs += delivery.runs_scored + (delivery.extras_runs || 0);
      if (delivery.is_wicket) stats.wickets++;
      if (delivery.extras_runs) stats.extras += delivery.extras_runs;
    });

    this.bowlingPerformances = Array.from(bowlerStats.values()).map(stats => {
      const overs = Math.floor(stats.balls / 6) + (stats.balls % 6) / 10;
      const economy = overs > 0 ? stats.runs / overs : 0;
      
      return {
        player: this.playersMap.get(stats.player_id.toString()) || { 
          public_id: stats.player_id.toString(), 
          full_name: 'Unknown Player' 
        } as PlayerSummary,
        overs: overs,
        maidens: stats.maidens,
        runs: stats.runs,
        wickets: stats.wickets,
        economy: economy,
        extras: stats.extras
      };
    }).sort((a, b) => b.wickets - a.wickets);
  }

  processFallOfWickets(deliveries: any[]): void {
    const wickets: FallOfWicket[] = [];
    let wicketCount = 0;
    let totalRuns = 0;

    deliveries.forEach((delivery: any) => {
      if (delivery.is_legal_delivery) {
        totalRuns += delivery.runs_scored;
      }
      
      if (delivery.is_wicket) {
        wicketCount++;
        const player = this.playersMap.get(delivery.batsman_id?.toString()) || { full_name: 'Unknown' } as PlayerSummary;
        const overs = Math.floor((delivery.over_number - 1) * 6 + delivery.ball_number) / 6;
        
        wickets.push({
          wicketNumber: wicketCount,
          runs: totalRuns,
          overs: parseFloat(overs.toFixed(1)),
          playerName: player.full_name || 'Unknown',
          dismissal: this.formatDismissal(delivery)
        });
      }
    });

    this.fallOfWickets = wickets;
  }

  processPartnerships(deliveries: any[]): void {
    // Simplified partnership tracking - this would need more complex logic in production
    this.partnerships = [];
  }

  processRunRateData(deliveries: any[]): void {
    const overData = new Map<number, number>();
    
    deliveries.forEach((delivery: any) => {
      const overNum = delivery.over_number;
      if (!overData.has(overNum)) {
        overData.set(overNum, 0);
      }
      if (delivery.is_legal_delivery) {
        overData.set(overNum, overData.get(overNum)! + delivery.runs_scored);
      }
    });

    let cumulative = 0;
    this.runRateData = Array.from(overData.entries())
      .sort(([a], [b]) => a - b)
      .map(([over, runs]) => {
        cumulative += runs;
        return { over, runs, cumulative };
      });
  }

  formatDismissal(delivery: any): string {
    if (!delivery.dismissal_type) return 'not out';
    
    const type = delivery.dismissal_type.toLowerCase().replace('_', ' ');
    const bowler = this.playersMap.get(delivery.bowler_id?.toString());
    const fielder = delivery.fielder_id ? this.playersMap.get(delivery.fielder_id.toString()) : null;
    
    if (delivery.dismissal_type === 'CAUGHT' && fielder && bowler) {
      return `c ${fielder.full_name} b ${bowler?.full_name || 'Unknown'}`;
    } else if (delivery.dismissal_type === 'BOWLED' && bowler) {
      return `b ${bowler.full_name || 'Unknown'}`;
    } else if (delivery.dismissal_type === 'LBW' && bowler) {
      return `lbw b ${bowler.full_name || 'Unknown'}`;
    } else if (delivery.dismissal_type === 'RUN_OUT' && fielder) {
      return `run out (${fielder.full_name})`;
    }
    
    return type;
  }

  selectInnings(index: number): void {
    this.loadInningsDetails(index);
  }

  getTeamName(teamId: string | number | undefined): string {
    if (!teamId) return 'Unknown';
    const team = this.teamsMap.get(teamId.toString());
    return team?.name || 'Unknown Team';
  }

  getMaxValue(data: number[]): number {
    return Math.max(...data, 1);
  }

  getChartHeight(value: number, max: number): number {
    return (value / max) * 100;
  }

  getRunRateChartHeight(value: number): number {
    const max = Math.max(...this.runRateData.map(d => d.runs), 1);
    return (value / max) * 100;
  }

  formatDate(dateString: string | undefined): string {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  }

  getMatchResult(): string {
    if (!this.match) return '';
    
    if (this.match.result_type && this.match.winning_team_id) {
      const winningTeam = this.getTeamName(this.match.winning_team_id);
      return `${winningTeam} won by ${this.match.result_margin || 'a margin'}`;
    }
    
    if (this.match.status === 'LIVE') return 'Match in progress';
    if (this.match.status === 'SCHEDULED') return 'Match scheduled';
    
    return 'Result not available';
  }
}
