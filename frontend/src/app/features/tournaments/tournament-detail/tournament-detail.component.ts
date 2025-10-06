import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, ActivatedRoute } from '@angular/router';
import { Tournament } from '../../../core/models';
import { TournamentService } from '../../../core/services/tournament.service';

@Component({
  selector: 'app-tournament-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './tournament-detail.component.html',
  styleUrl: './tournament-detail.component.scss'
})
export class TournamentDetailComponent implements OnInit {
  tournament: Tournament | null = null;
  loading = false;
  error: string | null = null;
  showDeleteModal = false;
  deleting = false;

  constructor(
    private tournamentService: TournamentService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const tournamentId = this.route.snapshot.paramMap.get('id');
    if (tournamentId) {
      this.loadTournament(tournamentId);
    }
  }

  loadTournament(tournamentId: string): void {
    this.loading = true;
    this.error = null;

    this.tournamentService.getById(tournamentId).subscribe({
      next: (tournament) => {
        this.tournament = tournament;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load tournament';
        this.loading = false;
        console.error('Error loading tournament:', err);
      }
    });
  }

  onEdit(): void {
    if (this.tournament) {
      this.router.navigate(['/tournaments', this.tournament.public_id, 'edit']);
    }
  }

  onDelete(): void {
    this.showDeleteModal = true;
  }

  confirmDelete(): void {
    if (!this.tournament) return;

    this.deleting = true;
    this.tournamentService.delete(this.tournament.public_id).subscribe({
      next: () => {
        this.router.navigate(['/tournaments']);
      },
      error: (err) => {
        this.error = 'Failed to delete tournament';
        this.deleting = false;
        this.showDeleteModal = false;
        console.error('Error deleting tournament:', err);
      }
    });
  }

  cancelDelete(): void {
    this.showDeleteModal = false;
  }

  onBack(): void {
    this.router.navigate(['/tournaments']);
  }

  getTournamentInitials(name: string): string {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .substring(0, 2)
      .toUpperCase();
  }

  formatDate(dateString: string | undefined): string {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  }

  getDuration(): string {
    if (!this.tournament?.start_date || !this.tournament?.end_date) {
      return 'Duration not set';
    }
    
    const start = new Date(this.tournament.start_date);
    const end = new Date(this.tournament.end_date);
    const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    
    return `${days} day${days !== 1 ? 's' : ''}`;
  }

  getStatus(): { label: string; color: string } {
    if (!this.tournament?.start_date || !this.tournament?.end_date) {
      return { label: 'Draft', color: 'gray' };
    }

    const now = new Date();
    const start = new Date(this.tournament.start_date);
    const end = new Date(this.tournament.end_date);

    if (now < start) {
      return { label: 'Upcoming', color: 'blue' };
    } else if (now >= start && now <= end) {
      return { label: 'Ongoing', color: 'green' };
    } else {
      return { label: 'Completed', color: 'gray' };
    }
  }

  formatPointsSystem(pointsSystem: Record<string, any> | undefined): string {
    if (!pointsSystem) return 'Not configured';
    return JSON.stringify(pointsSystem, null, 2);
  }
}
