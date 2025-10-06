import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, ActivatedRoute } from '@angular/router';
import { Team } from '../../../core/models';
import { TeamService } from '../../../core/services/team.service';

@Component({
  selector: 'app-team-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './team-detail.component.html',
  styleUrl: './team-detail.component.scss'
})
export class TeamDetailComponent implements OnInit {
  team: Team | null = null;
  loading = false;
  error: string | null = null;
  showDeleteModal = false;
  deleting = false;

  constructor(
    private teamService: TeamService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const teamId = this.route.snapshot.paramMap.get('id');
    if (teamId) {
      this.loadTeam(teamId);
    }
  }

  loadTeam(teamId: string): void {
    this.loading = true;
    this.error = null;

    this.teamService.getById(teamId).subscribe({
      next: (team) => {
        this.team = team;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load team';
        this.loading = false;
        console.error('Error loading team:', err);
      }
    });
  }

  onEdit(): void {
    if (this.team) {
      this.router.navigate(['/teams', this.team.public_id, 'edit']);
    }
  }

  onDelete(): void {
    this.showDeleteModal = true;
  }

  confirmDelete(): void {
    if (!this.team) return;

    this.deleting = true;
    this.teamService.delete(this.team.public_id).subscribe({
      next: () => {
        this.router.navigate(['/teams']);
      },
      error: (err) => {
        this.error = 'Failed to delete team';
        this.deleting = false;
        this.showDeleteModal = false;
        console.error('Error deleting team:', err);
      }
    });
  }

  cancelDelete(): void {
    this.showDeleteModal = false;
  }

  getTeamInitials(teamName: string): string {
    return teamName
      .split(' ')
      .map(word => word[0])
      .join('')
      .substring(0, 2)
      .toUpperCase();
  }

  getCountryFlag(countryCode: string | undefined): string {
    if (!countryCode || countryCode.length !== 3) return '🏏';
    
    const countryFlags: Record<string, string> = {
      'IND': '🇮🇳', 'AUS': '🇦🇺', 'ENG': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'PAK': '🇵🇰',
      'NZL': '🇳🇿', 'RSA': '🇿🇦', 'WI': '🏴', 'SRI': '🇱🇰',
      'BAN': '🇧🇩', 'AFG': '🇦🇫', 'IRE': '🇮🇪', 'ZIM': '🇿🇼'
    };
    
    return countryFlags[countryCode.toUpperCase()] || '🏏';
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}
