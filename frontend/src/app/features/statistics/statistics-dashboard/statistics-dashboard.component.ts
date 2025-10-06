import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { forkJoin } from 'rxjs';
import { TeamService } from '../../../core/services/team.service';
import { PlayerService } from '../../../core/services/player.service';
import { MatchService } from '../../../core/services/match.service';
import { TournamentService } from '../../../core/services/tournament.service';

interface DashboardStats {
  totalTeams: number;
  totalPlayers: number;
  totalMatches: number;
  totalTournaments: number;
}

interface RecentMatch {
  id: string;
  team1: string;
  team2: string;
  result: string;
  date: string;
  venue: string;
}

interface TopPerformer {
  id: string;
  name: string;
  team: string;
  stats: string;
  photo?: string;
}

interface ChartData {
  labels: string[];
  data: number[];
}

@Component({
  selector: 'app-statistics-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './statistics-dashboard.component.html',
  styleUrl: './statistics-dashboard.component.scss'
})
export class StatisticsDashboardComponent implements OnInit {
  loading = true;
  error: string | null = null;

  stats: DashboardStats = {
    totalTeams: 0,
    totalPlayers: 0,
    totalMatches: 0,
    totalTournaments: 0
  };

  recentMatches: RecentMatch[] = [];
  upcomingMatches: RecentMatch[] = [];
  topBatsmen: TopPerformer[] = [];
  topBowlers: TopPerformer[] = [];
  
  matchesByType: ChartData = { labels: [], data: [] };
  teamsByCountry: ChartData = { labels: [], data: [] };

  constructor(
    private teamService: TeamService,
    private playerService: PlayerService,
    private matchService: MatchService,
    private tournamentService: TournamentService
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.loading = true;
    this.error = null;

    forkJoin({
      teams: this.teamService.getAll({ limit: 1000 }),
      players: this.playerService.getAll({ limit: 1000 }),
      matches: this.matchService.getAll({ limit: 100 }),
      tournaments: this.tournamentService.getAll({ limit: 1000 })
    }).subscribe({
      next: (data) => {
        // Update stats
        this.stats.totalTeams = data.teams.total;
        this.stats.totalPlayers = data.players.total;
        this.stats.totalMatches = data.matches.total;
        this.stats.totalTournaments = data.tournaments.total;

        // Process matches for recent/upcoming
        this.processMatches(data.matches.items);

        // Process teams for country distribution
        this.processTeamsByCountry(data.teams.items);

        // Process matches by type
        this.processMatchesByType(data.matches.items);

        // Generate top performers (mock data for now - would come from stats API)
        this.generateTopPerformers(data.players.items);

        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load dashboard data';
        this.loading = false;
        console.error('Error loading dashboard:', err);
      }
    });
  }

  processMatches(matches: any[]): void {
    const now = new Date();
    
    // Recent matches (completed, past dates)
    this.recentMatches = matches
      .filter(m => m.start_time && new Date(m.start_time) < now)
      .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime())
      .slice(0, 5)
      .map(m => ({
        id: m.public_id,
        team1: this.getTeamName(m, 0),
        team2: this.getTeamName(m, 1),
        result: m.result || 'Completed',
        date: this.formatDate(m.start_time),
        venue: m.venue?.name || 'TBA'
      }));

    // Upcoming matches (future dates)
    this.upcomingMatches = matches
      .filter(m => m.start_time && new Date(m.start_time) >= now)
      .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
      .slice(0, 5)
      .map(m => ({
        id: m.public_id,
        team1: this.getTeamName(m, 0),
        team2: this.getTeamName(m, 1),
        result: 'vs',
        date: this.formatDate(m.start_time),
        venue: m.venue?.name || 'TBA'
      }));
  }

  getTeamName(match: any, index: number): string {
    if (match.teams && match.teams[index]) {
      return match.teams[index].short_name || match.teams[index].name || 'TBA';
    }
    return 'TBA';
  }

  processTeamsByCountry(teams: any[]): void {
    const countryCount = teams.reduce((acc, team) => {
      const country = team.country_code || 'Unknown';
      acc[country] = (acc[country] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const sorted = Object.entries(countryCount)
      .sort(([, a], [, b]) => (b as number) - (a as number))
      .slice(0, 8);

    this.teamsByCountry = {
      labels: sorted.map(([country]) => country),
      data: sorted.map(([, count]) => count as number)
    };
  }

  processMatchesByType(matches: any[]): void {
    const typeCount = matches.reduce((acc, match) => {
      const type = match.match_type || 'Unknown';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    this.matchesByType = {
      labels: Object.keys(typeCount),
      data: Object.values(typeCount)
    };
  }

  generateTopPerformers(players: any[]): void {
    // Mock top performers - in production would come from stats API
    const shuffled = [...players].sort(() => 0.5 - Math.random());
    
    this.topBatsmen = shuffled.slice(0, 5).map((player, index) => ({
      id: player.public_id,
      name: player.full_name || player.known_as,
      team: 'Team ' + (index + 1),
      stats: `${1000 + index * 100} runs @ ${45 + index}.${20 + index * 5} avg`,
      photo: undefined
    }));

    this.topBowlers = shuffled.slice(5, 10).map((player, index) => ({
      id: player.public_id,
      name: player.full_name || player.known_as,
      team: 'Team ' + (index + 1),
      stats: `${50 - index * 5} wkts @ ${22 - index}.${50 + index * 10} avg`,
      photo: undefined
    }));
  }

  formatDate(dateString: string): string {
    if (!dateString) return 'TBA';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  }

  getInitials(name: string): string {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .substring(0, 2)
      .toUpperCase();
  }

  getChartHeight(value: number, max: number): number {
    return (value / max) * 100;
  }

  getMaxValue(data: number[]): number {
    return Math.max(...data, 1);
  }
}
