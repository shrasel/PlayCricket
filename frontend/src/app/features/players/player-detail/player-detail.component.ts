import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { PlayerService } from '../../../core/services/player.service';
import { Player } from '../../../core/models';

@Component({
  selector: 'app-player-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './player-detail.component.html',
  styleUrl: './player-detail.component.scss'
})
export class PlayerDetailComponent implements OnInit {
  player: Player | null = null;
  loading = false;
  error: string | null = null;
  showDeleteModal = false;
  deleting = false;

  constructor(
    private playerService: PlayerService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadPlayer(id);
    }
  }

  loadPlayer(id: string): void {
    this.loading = true;
    this.playerService.getById(id).subscribe({
      next: (player) => {
        this.player = player;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load player details';
        this.loading = false;
        console.error('Error loading player:', err);
      }
    });
  }

  onEdit(): void {
    if (this.player) {
      this.router.navigate(['/players', this.player.public_id, 'edit']);
    }
  }

  onDelete(): void {
    this.showDeleteModal = true;
  }

  confirmDelete(): void {
    if (this.player) {
      this.deleting = true;
      this.playerService.delete(this.player.public_id).subscribe({
        next: () => {
          this.deleting = false;
          this.showDeleteModal = false;
          this.router.navigate(['/players']);
        },
        error: (err) => {
          this.error = 'Failed to delete player';
          this.deleting = false;
          this.showDeleteModal = false;
          console.error('Error deleting player:', err);
        }
      });
    }
  }

  cancelDelete(): void {
    this.showDeleteModal = false;
  }

  getPlayerInitials(fullName: string): string {
    return fullName
      .split(' ')
      .map(word => word[0])
      .join('')
      .substring(0, 2)
      .toUpperCase();
  }

  calculateAge(dob: string | undefined): number | null {
    if (!dob) return null;
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  }
}
