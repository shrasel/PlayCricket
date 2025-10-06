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
  loading = false;
  error: string | null = null;
  
  // Filters
  searchTerm = '';
  countryFilter = '';
  
  // Pagination
  currentPage = 1;
  pageSize = 12;
  totalTeams = 0;

  constructor(private teamService: TeamService) {}

  ngOnInit(): void {
    this.loadTeams();
  }

  loadTeams(): void {
    this.loading = true;
    this.error = null;
    
    const skip = (this.currentPage - 1) * this.pageSize;
    
    this.teamService.getAll({ skip, limit: this.pageSize }).subscribe({
      next: (response) => {
        this.teams = response.items;
        this.totalTeams = response.total;
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
      const matchesSearch = !this.searchTerm || 
        team.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        team.short_name.toLowerCase().includes(this.searchTerm.toLowerCase());
      
      const matchesCountry = !this.countryFilter || 
        team.country_code?.toLowerCase() === this.countryFilter.toLowerCase();
      
      return matchesSearch && matchesCountry;
    });
  }

  onSearchChange(): void {
    this.applyFilters();
  }

  onCountryFilterChange(): void {
    this.applyFilters();
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.countryFilter = '';
    this.applyFilters();
  }

  nextPage(): void {
    if (this.currentPage * this.pageSize < this.totalTeams) {
      this.currentPage++;
      this.loadTeams();
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadTeams();
    }
  }

  get totalPages(): number {
    return Math.ceil(this.totalTeams / this.pageSize);
  }

  get Math() {
    return Math;
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
