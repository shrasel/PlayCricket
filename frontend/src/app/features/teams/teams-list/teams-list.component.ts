import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Team } from '../../../core/models';
import { TeamService } from '../../../core/services/team.service';

@Component({
  selector: 'app-teams-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './teams-list.component.html',
  styleUrl: './teams-list.component.scss'
})
export class TeamsListComponent implements OnInit {
  teams: Team[] = [];
  filteredTeams: Team[] = [];
  paginatedTeams: Team[] = [];
  loading = false;
  error: string | null = null;
  
  // Filters
  searchQuery = '';
  selectedCountry = '';
  
  // Pagination
  currentPage = 1;
  pageSize = 12;

  constructor(private teamService: TeamService) {}

  ngOnInit(): void {
    this.loadTeams();
  }

  loadTeams(): void {
    this.loading = true;
    this.error = null;
    
    this.teamService.getAll({ skip: 0, limit: 1000 }).subscribe({
      next: (response) => {
        this.teams = response.items;
        this.applyFilters();
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load teams';
        this.loading = false;
        console.error('Error loading teams:', err);
      }
    });
  }

  applyFilters(): void {
    this.filteredTeams = this.teams.filter(team => {
      const matchesSearch = !this.searchQuery || 
        team.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        team.short_name.toLowerCase().includes(this.searchQuery.toLowerCase());
      
      const matchesCountry = !this.selectedCountry || 
        team.country_code?.toLowerCase() === this.selectedCountry.toLowerCase();
      
      return matchesSearch && matchesCountry;
    });
    
    this.currentPage = 1; // Reset to first page when filters change
    this.updatePagination();
  }

  clearFilters(): void {
    this.searchQuery = '';
    this.selectedCountry = '';
    this.applyFilters();
  }

  updatePagination(): void {
    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    this.paginatedTeams = this.filteredTeams.slice(start, end);
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.updatePagination();
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.updatePagination();
    }
  }

  goToPage(page: number): void {
    this.currentPage = page;
    this.updatePagination();
  }

  getPageNumbers(): number[] {
    const pages: number[] = [];
    const maxPagesToShow = 5;
    const totalPages = this.totalPages;
    
    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      const start = Math.max(1, this.currentPage - 2);
      const end = Math.min(totalPages, start + maxPagesToShow - 1);
      
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
    }
    
    return pages;
  }

  get totalPages(): number {
    return Math.ceil(this.filteredTeams.length / this.pageSize);
  }

  get Math() {
    return Math;
  }

  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = '';
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
    
    // Map common cricket playing nations (ISO 3166-1 alpha-3 to flag emoji)
    const countryFlags: Record<string, string> = {
      'IND': '🇮🇳', 'AUS': '🇦🇺', 'ENG': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'PAK': '🇵🇰',
      'NZL': '🇳🇿', 'RSA': '🇿🇦', 'WI': '🏴', 'SRI': '🇱🇰',
      'BAN': '🇧🇩', 'AFG': '🇦🇫', 'IRE': '🇮🇪', 'ZIM': '🇿🇼'
    };
    
    return countryFlags[countryCode.toUpperCase()] || '🏏';
  }
}
