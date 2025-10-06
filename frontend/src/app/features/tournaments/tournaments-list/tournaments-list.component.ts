import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Tournament } from '../../../core/models';
import { TournamentService } from '../../../core/services/tournament.service';

@Component({
  selector: 'app-tournaments-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './tournaments-list.component.html',
  styleUrl: './tournaments-list.component.scss'
})
export class TournamentsListComponent implements OnInit {
  tournaments: Tournament[] = [];
  filteredTournaments: Tournament[] = [];
  loading = false;
  error: string | null = null;
  
  // Filters
  searchTerm = '';
  matchTypeFilter = '';
  seasonFilter = '';
  
  // Pagination
  currentPage = 1;
  pageSize = 12;
  totalTournaments = 0;

  constructor(private tournamentService: TournamentService) {}

  ngOnInit(): void {
    this.loadTournaments();
  }

  loadTournaments(): void {
    this.loading = true;
    this.error = null;
    
    const skip = (this.currentPage - 1) * this.pageSize;
    
    this.tournamentService.getAll({ skip, limit: this.pageSize }).subscribe({
      next: (response) => {
        this.tournaments = response.items;
        this.totalTournaments = response.total;
        this.applyFilters();
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load tournaments';
        this.loading = false;
        console.error('Error loading tournaments:', err);
      }
    });
  }

  applyFilters(): void {
    this.filteredTournaments = this.tournaments.filter(tournament => {
      const matchesSearch = !this.searchTerm || 
        tournament.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        tournament.short_name?.toLowerCase().includes(this.searchTerm.toLowerCase());
      
      const matchesType = !this.matchTypeFilter || 
        tournament.match_type?.toLowerCase() === this.matchTypeFilter.toLowerCase();
      
      const matchesSeason = !this.seasonFilter || 
        tournament.season?.toLowerCase().includes(this.seasonFilter.toLowerCase());
      
      return matchesSearch && matchesType && matchesSeason;
    });
    this.currentPage = 1; // Reset to first page when filters change
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.matchTypeFilter = '';
    this.seasonFilter = '';
    this.applyFilters();
  }

  getPaginatedTournaments(): Tournament[] {
    const startIndex = (this.currentPage - 1) * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    return this.filteredTournaments.slice(startIndex, endIndex);
  }

  getTotalPages(): number {
    return Math.ceil(this.filteredTournaments.length / this.pageSize);
  }

  getPageNumbers(): number[] {
    const totalPages = this.getTotalPages();
    const pages: number[] = [];
    const maxPagesToShow = 5;
    
    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      const startPage = Math.max(1, this.currentPage - 2);
      const endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);
      
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
    }
    
    return pages;
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.getTotalPages()) {
      this.currentPage = page;
    }
  }

  get Math() {
    return Math;
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
    if (!dateString) return 'TBD';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  }
}
