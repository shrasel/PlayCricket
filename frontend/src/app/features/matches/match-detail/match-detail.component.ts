import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { MatchService } from '@core/services/match.service';
import { Match, MatchStatus, TossInfo } from '@core/models';

@Component({
  selector: 'app-match-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './match-detail.component.html',
  styleUrl: './match-detail.component.scss'
})
export class MatchDetailComponent implements OnInit {
  match: Match | null = null;
  loading = false;
  error: string | null = null;
  showDeleteConfirm = false;
  showTossModal = false;
  updatingStatus = false;

  // Enums
  MatchStatus = MatchStatus;
  statusOptions = Object.values(MatchStatus);

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private matchService: MatchService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const matchId = params['id'];
      if (matchId) {
        this.loadMatch(matchId);
      }
    });
  }

  loadMatch(id: string): void {
    this.loading = true;
    this.error = null;

    this.matchService.getById(id).subscribe({
      next: (match: Match) => {
        this.match = match;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load match details';
        console.error('Error loading match:', err);
        this.loading = false;
      }
    });
  }

  getStatusBadgeClass(status: MatchStatus): string {
    const baseClasses = 'px-4 py-2 rounded-full text-sm font-semibold inline-block';
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

  formatDate(dateString: string | undefined): string {
    if (!dateString) return 'Not scheduled';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  formatShortDate(dateString: string | undefined): string {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }

  updateStatus(newStatus: MatchStatus): void {
    if (!this.match) return;

    this.updatingStatus = true;
    this.matchService.updateMatchStatus(this.match.public_id, newStatus).subscribe({
      next: (updatedMatch: Match) => {
        this.match = updatedMatch;
        this.updatingStatus = false;
      },
      error: (err) => {
        console.error('Error updating status:', err);
        alert('Failed to update match status');
        this.updatingStatus = false;
      }
    });
  }

  editMatch(): void {
    if (this.match) {
      this.router.navigate(['/matches', this.match.public_id, 'edit']);
    }
  }

  confirmDelete(): void {
    this.showDeleteConfirm = true;
  }

  cancelDelete(): void {
    this.showDeleteConfirm = false;
  }

  deleteMatch(): void {
    if (!this.match) return;

    this.matchService.delete(this.match.public_id).subscribe({
      next: () => {
        this.router.navigate(['/matches']);
      },
      error: (err) => {
        console.error('Error deleting match:', err);
        alert('Failed to delete match');
        this.showDeleteConfirm = false;
      }
    });
  }

  getTeamName(index: number): string {
    if (!this.match || !this.match.teams || this.match.teams.length <= index) {
      return 'TBD';
    }
    return this.match.teams[index].name;
  }

  getTeamShortName(index: number): string {
    if (!this.match || !this.match.teams || this.match.teams.length <= index) {
      return 'TBD';
    }
    return this.match.teams[index].short_name;
  }

  getTeamLogo(index: number): string | undefined {
    if (!this.match || !this.match.teams || this.match.teams.length <= index) {
      return undefined;
    }
    return this.match.teams[index].logo_url;
  }

  backToList(): void {
    this.router.navigate(['/matches']);
  }
}
