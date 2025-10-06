import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { MatchService } from '../../../core/services/match.service';
import { Match, MatchStatus } from '../../../core/models';

@Component({
  selector: 'app-match-selector',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './match-selector.component.html',
  styleUrl: './match-selector.component.scss'
})
export class MatchSelectorComponent implements OnInit {
  matches: Match[] = [];
  filteredMatches: Match[] = [];
  loading = true;
  error: string | null = null;
  
  selectedStatus: string = 'LIVE';
  searchTerm = '';

  constructor(
    private matchService: MatchService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadMatches();
  }

  loadMatches(): void {
    this.loading = true;
    this.error = null;

    this.matchService.getAll({ limit: 100 }).subscribe({
      next: (response) => {
        this.matches = response.items || [];
        this.applyFilters();
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to load matches';
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    this.filteredMatches = this.matches.filter(match => {
      const statusMatch = this.selectedStatus === 'ALL' || match.status === this.selectedStatus;
      
      const searchMatch = this.searchTerm === '' || 
        (match.teams?.some(team => 
          team.name?.toLowerCase().includes(this.searchTerm.toLowerCase())
        )) ||
        (match.venue?.name?.toLowerCase().includes(this.searchTerm.toLowerCase()));

      return statusMatch && searchMatch;
    });
  }

  onStatusChange(): void {
    this.applyFilters();
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  selectMatch(match: Match): void {
    if (match.public_id) {
      this.router.navigate(['/live-scoring', match.public_id]);
    }
  }

  getStatusBadgeClass(status: MatchStatus): string {
    const classes: Record<MatchStatus, string> = {
      'SCHEDULED': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      'LIVE': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 animate-pulse',
      'COMPLETED': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
      'ABANDONED': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      'CANCELLED': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
  }

  getTeamName(match: Match, index: number): string {
    if (match.teams && match.teams.length > index) {
      return match.teams[index].name || 'Unknown Team';
    }
    return `Team ${index + 1}`;
  }

  formatDate(dateString: string | undefined): string {
    if (!dateString) return 'Not scheduled';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  canScore(match: Match): boolean {
    return match.status === 'SCHEDULED' || match.status === 'LIVE';
  }
}
