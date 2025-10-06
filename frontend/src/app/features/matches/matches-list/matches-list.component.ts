import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatchService } from '@core/services/match.service';
import { Match, MatchStatus, MatchType, PaginatedResponse } from '@core/models';

@Component({
  selector: 'app-matches-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './matches-list.component.html',
  styleUrl: './matches-list.component.scss'
})
export class MatchesListComponent implements OnInit {
  matches: Match[] = [];
  loading = false;
  error: string | null = null;

  // Pagination
  currentPage = 1;
  pageSize = 10;
  totalMatches = 0;
  totalPages = 0;

  // Filters
  statusFilter: MatchStatus | '' = '';
  matchTypeFilter: MatchType | '' = '';
  searchQuery = '';

  // Enums for template
  MatchStatus = MatchStatus;
  MatchType = MatchType;

  // Dropdown options
  statusOptions = Object.values(MatchStatus);
  matchTypeOptions = Object.values(MatchType);

  constructor(private matchService: MatchService) {}

  ngOnInit(): void {
    this.loadMatches();
  }

  loadMatches(): void {
    this.loading = true;
    this.error = null;

    const params: any = {
      skip: (this.currentPage - 1) * this.pageSize,
      limit: this.pageSize
    };

    if (this.statusFilter) {
      params.status = this.statusFilter;
    }

    this.matchService.getAll(params).subscribe({
      next: (response: PaginatedResponse<Match>) => {
        this.matches = response.items;
        this.totalMatches = response.total;
        this.totalPages = Math.ceil(this.totalMatches / this.pageSize);
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load matches. Please try again.';
        console.error('Error loading matches:', err);
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    this.currentPage = 1;
    this.loadMatches();
  }

  clearFilters(): void {
    this.statusFilter = '';
    this.matchTypeFilter = '';
    this.searchQuery = '';
    this.currentPage = 1;
    this.loadMatches();
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.loadMatches();
    }
  }

  nextPage(): void {
    this.goToPage(this.currentPage + 1);
  }

  previousPage(): void {
    this.goToPage(this.currentPage - 1);
  }

  getStatusBadgeClass(status: MatchStatus): string {
    const baseClasses = 'px-3 py-1 rounded-full text-xs font-semibold';
    switch (status) {
      case MatchStatus.SCHEDULED:
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case MatchStatus.LIVE:
        return `${baseClasses} bg-green-100 text-green-800 animate-pulse`;
      case MatchStatus.COMPLETED:
        return `${baseClasses} bg-gray-100 text-gray-800`;
      case MatchStatus.ABANDONED:
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case MatchStatus.CANCELLED:
        return `${baseClasses} bg-red-100 text-red-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  }

  getMatchTypeLabel(type: MatchType): string {
    return type.replace('_', ' ');
  }

  formatDate(dateString: string | undefined): string {
    if (!dateString) return 'TBD';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getTeamsDisplay(match: Match): string {
    if (!match.teams || match.teams.length === 0) {
      return 'TBD vs TBD';
    }
    if (match.teams.length === 1) {
      return `${match.teams[0].short_name} vs TBD`;
    }
    return `${match.teams[0].short_name} vs ${match.teams[1].short_name}`;
  }
}
