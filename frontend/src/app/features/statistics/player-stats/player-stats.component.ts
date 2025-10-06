import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { forkJoin } from 'rxjs';

import { PlayerService } from '../../../core/services/player.service';
import { MatchService } from '../../../core/services/match.service';
import { InningsService } from '../../../core/services/innings.service';
import { DeliveryService } from '../../../core/services/delivery.service';

import {
  Player,
  Match,
  Delivery,
  TeamSummary,
  CareerStats
} from '../../../core/models';

interface FormatStats {
  format: string;
  matches: number;
  innings: number;
  runs: number;
  wickets: number;
  average: number;
  strikeRate: number;
  economy: number;
  highestScore?: number;
  bestFigures?: string;
}

interface RecentMatchPerformance {
  matchId: string;
  opponent: string;
  date: string;
  runs: number;
  wickets: number;
  result: string;
}

interface TrendData {
  label: string;
  value: number;
}

@Component({
  selector: 'app-player-stats',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './player-stats.component.html',
  styleUrl: './player-stats.component.scss'
})
export class PlayerStatsComponent implements OnInit {
  playerId: string = '';
  loading = true;
  error: string | null = null;

  player: Player | null = null;
  
  // Career summary
  totalMatches = 0;
  totalInnings = 0;
  totalRuns = 0;
  totalWickets = 0;
  battingAverage = 0;
  bowlingAverage = 0;
  battingStrikeRate = 0;
  bowlingEconomy = 0;
  highestScore = 0;
  bestBowlingFigures = '0/0';

  // Format-wise stats
  formatStats: FormatStats[] = [];
  
  // Recent matches
  recentMatches: RecentMatchPerformance[] = [];
  
  // Trend data
  runsTrend: TrendData[] = [];
  wicketsTrend: TrendData[] = [];

  constructor(
    private route: ActivatedRoute,
    private playerService: PlayerService,
    private matchService: MatchService,
    private inningsService: InningsService,
    private deliveryService: DeliveryService
  ) {}

  ngOnInit(): void {
    this.playerId = this.route.snapshot.paramMap.get('id') || '';
    if (this.playerId) {
      this.loadPlayerData();
    } else {
      this.error = 'Invalid player ID';
      this.loading = false;
    }
  }

  loadPlayerData(): void {
    this.loading = true;
    this.error = null;

    forkJoin({
      player: this.playerService.getById(this.playerId),
      matches: this.matchService.getAll({ limit: 100 }),
      deliveries: this.deliveryService.getAll({ limit: 10000 })
    }).subscribe({
      next: (data) => {
        this.player = data.player;
        
        // Filter deliveries for this player
        const playerDeliveries = (data.deliveries.items || []).filter((d: any) => 
          d.batsman_id?.toString() === this.player?.id?.toString() || 
          d.bowler_id?.toString() === this.player?.id?.toString()
        );

        this.processCareerStats(playerDeliveries);
        this.processFormatStats(playerDeliveries, data.matches.items || []);
        this.processRecentMatches(playerDeliveries, data.matches.items || []);
        this.processTrendData(playerDeliveries);
        
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to load player data';
        this.loading = false;
      }
    });
  }

  processCareerStats(deliveries: any[]): void {
    let runsScored = 0;
    let ballsFaced = 0;
    let wicketsTaken = 0;
    let runsConceded = 0;
    let ballsBowled = 0;
    let timesOut = 0;
    let highScore = 0;

    // Track innings
    const inningsSet = new Set<string>();
    
    deliveries.forEach((d: any) => {
      // Batting stats
      if (d.batsman_id?.toString() === this.player?.id?.toString()) {
        inningsSet.add(`${d.innings_id}_bat`);
        if (d.is_legal_delivery) {
          runsScored += d.runs_scored;
          ballsFaced++;
        }
        if (d.is_wicket) timesOut++;
      }
      
      // Bowling stats
      if (d.bowler_id?.toString() === this.player?.id?.toString()) {
        inningsSet.add(`${d.innings_id}_bowl`);
        if (d.is_legal_delivery) {
          runsConceded += d.runs_scored;
          ballsBowled++;
        }
        runsConceded += (d.extras_runs || 0);
        if (d.is_wicket) wicketsTaken++;
      }
    });

    this.totalInnings = inningsSet.size;
    this.totalRuns = runsScored;
    this.totalWickets = wicketsTaken;
    this.battingAverage = timesOut > 0 ? runsScored / timesOut : runsScored;
    this.battingStrikeRate = ballsFaced > 0 ? (runsScored / ballsFaced) * 100 : 0;
    this.bowlingAverage = wicketsTaken > 0 ? runsConceded / wicketsTaken : 0;
    this.bowlingEconomy = ballsBowled > 0 ? (runsConceded / (ballsBowled / 6)) : 0;
    this.highestScore = highScore;
  }

  processFormatStats(deliveries: any[], matches: any[]): void {
    const formats = ['TEST', 'ODI', 'T20'];
    this.formatStats = [];

    formats.forEach(format => {
      const formatMatches = matches.filter((m: any) => m.match_type === format);
      const matchIds = new Set(formatMatches.map((m: any) => m.id));
      
      const formatDeliveries = deliveries.filter((d: any) => {
        // We'd need to look up innings to match to get match_id
        // For now, this is simplified
        return matchIds.has(d.match_id);
      });

      let runs = 0;
      let balls = 0;
      let wickets = 0;
      let runsConceded = 0;
      let ballsBowled = 0;

      formatDeliveries.forEach((d: any) => {
        if (d.batsman_id?.toString() === this.player?.id?.toString() && d.is_legal_delivery) {
          runs += d.runs_scored;
          balls++;
        }
        if (d.bowler_id?.toString() === this.player?.id?.toString()) {
          if (d.is_legal_delivery) {
            runsConceded += d.runs_scored;
            ballsBowled++;
          }
          if (d.is_wicket) wickets++;
        }
      });

      const overs = ballsBowled / 6;
      
      this.formatStats.push({
        format: format,
        matches: formatMatches.length,
        innings: formatMatches.length,
        runs: runs,
        wickets: wickets,
        average: balls > 0 ? runs / (balls / 100) : 0,
        strikeRate: balls > 0 ? (runs / balls) * 100 : 0,
        economy: overs > 0 ? runsConceded / overs : 0
      });
    });
  }

  processRecentMatches(deliveries: any[], matches: any[]): void {
    // Group deliveries by innings/match
    const matchPerformance = new Map<number, any>();

    deliveries.forEach((d: any) => {
      if (!matchPerformance.has(d.innings_id)) {
        matchPerformance.set(d.innings_id, {
          innings_id: d.innings_id,
          runs: 0,
          wickets: 0
        });
      }

      const perf = matchPerformance.get(d.innings_id);
      if (d.batsman_id?.toString() === this.player?.id?.toString() && d.is_legal_delivery) {
        perf.runs += d.runs_scored;
      }
      if (d.bowler_id?.toString() === this.player?.id?.toString() && d.is_wicket) {
        perf.wickets++;
      }
    });

    // Convert to recent matches (mock data for demo)
    this.recentMatches = Array.from(matchPerformance.values())
      .slice(0, 10)
      .map((perf, index) => ({
        matchId: perf.innings_id.toString(),
        opponent: 'Team ' + (index + 1),
        date: new Date(Date.now() - index * 7 * 24 * 60 * 60 * 1000).toLocaleDateString(),
        runs: perf.runs,
        wickets: perf.wickets,
        result: index % 2 === 0 ? 'Won' : 'Lost'
      }));
  }

  processTrendData(deliveries: any[]): void {
    // Group by match/innings for trend
    const inningsPerformance = new Map<string, { runs: number; wickets: number }>();

    deliveries.forEach((d: any) => {
      const key = d.innings_id.toString();
      if (!inningsPerformance.has(key)) {
        inningsPerformance.set(key, { runs: 0, wickets: 0 });
      }

      const perf = inningsPerformance.get(key)!;
      if (d.batsman_id?.toString() === this.player?.id?.toString() && d.is_legal_delivery) {
        perf.runs += d.runs_scored;
      }
      if (d.bowler_id?.toString() === this.player?.id?.toString() && d.is_wicket) {
        perf.wickets++;
      }
    });

    const performances = Array.from(inningsPerformance.entries())
      .slice(0, 10)
      .reverse();

    this.runsTrend = performances.map(([key, perf], index) => ({
      label: `Match ${index + 1}`,
      value: perf.runs
    }));

    this.wicketsTrend = performances.map(([key, perf], index) => ({
      label: `Match ${index + 1}`,
      value: perf.wickets
    }));
  }

  getInitials(name: string | undefined): string {
    if (!name) return 'N/A';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  }

  getMaxValue(data: TrendData[]): number {
    if (data.length === 0) return 1;
    return Math.max(...data.map(d => d.value), 1);
  }

  getChartHeight(value: number, max: number): number {
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

  getRoleDisplay(): string {
    if (!this.player) return 'N/A';
    
    // Determine role based on batting and bowling styles
    if (this.player.batting_style && this.player.bowling_style) {
      return 'All Rounder';
    } else if (this.player.batting_style) {
      return 'Batsman';
    } else if (this.player.bowling_style) {
      return 'Bowler';
    }
    return 'Player';
  }

  getPlayerAge(): number {
    if (!this.player?.dob) return 0;
    
    const dob = new Date(this.player.dob);
    const ageDiff = Date.now() - dob.getTime();
    const ageDate = new Date(ageDiff);
    return Math.abs(ageDate.getUTCFullYear() - 1970);
  }
}
