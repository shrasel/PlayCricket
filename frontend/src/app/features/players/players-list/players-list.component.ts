import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Player } from '../../../core/models';
import { PlayerService } from '../../../core/services/player.service';

@Component({
  selector: 'app-players-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './players-list.component.html',
  styleUrl: './players-list.component.scss'
})
export class PlayersListComponent implements OnInit {
  players: Player[] = [];
  filteredPlayers: Player[] = [];
  loading = false;
  error: string | null = null;
  
  // Filters
  searchTerm = '';
  battingStyleFilter = '';
  bowlingStyleFilter = '';
  
  // Pagination
  currentPage = 1;
  pageSize = 12;
  totalPlayers = 0;

  constructor(private playerService: PlayerService) {}

  ngOnInit(): void {
    this.loadPlayers();
  }

  loadPlayers(): void {
    this.loading = true;
    this.error = null;
    
    const skip = (this.currentPage - 1) * this.pageSize;
    
    this.playerService.getAll({ skip, limit: this.pageSize }).subscribe({
      next: (response) => {
        this.players = response.items;
        this.totalPlayers = response.total;
        this.applyFilters();
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load players';
        this.loading = false;
        console.error('Error loading players:', err);
      }
    });
  }

  applyFilters(): void {
    this.filteredPlayers = this.players.filter(player => {
      const matchesSearch = !this.searchTerm || 
        player.full_name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        player.known_as?.toLowerCase().includes(this.searchTerm.toLowerCase());
      
      const matchesBattingStyle = !this.battingStyleFilter || 
        player.batting_style?.toLowerCase() === this.battingStyleFilter.toLowerCase();
      
      const matchesBowlingStyle = !this.bowlingStyleFilter || 
        player.bowling_style?.toLowerCase().includes(this.bowlingStyleFilter.toLowerCase());
      
      return matchesSearch && matchesBattingStyle && matchesBowlingStyle;
    });
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  onBattingStyleChange(): void {
    this.applyFilters();
  }

  onBowlingStyleChange(): void {
    this.applyFilters();
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.battingStyleFilter = '';
    this.bowlingStyleFilter = '';
    this.applyFilters();
  }

  nextPage(): void {
    if (this.currentPage * this.pageSize < this.totalPlayers) {
      this.currentPage++;
      this.loadPlayers();
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadPlayers();
    }
  }

  get totalPages(): number {
    return Math.ceil(this.totalPlayers / this.pageSize);
  }

  get Math() {
    return Math;
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
}
