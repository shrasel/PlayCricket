import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Venue } from '../../../core/models';
import { VenueService } from '../../../core/services/venue.service';

@Component({
  selector: 'app-venues-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './venues-list.component.html',
  styleUrl: './venues-list.component.scss'
})
export class VenuesListComponent implements OnInit {
  venues: Venue[] = [];
  filteredVenues: Venue[] = [];
  loading = false;
  error: string | null = null;
  
  // Filters
  searchTerm = '';
  countryFilter = '';
  
  // Pagination
  currentPage = 1;
  pageSize = 12;
  totalVenues = 0;

  constructor(private venueService: VenueService) {}

  ngOnInit(): void {
    this.loadVenues();
  }

  loadVenues(): void {
    this.loading = true;
    this.error = null;
    
    const skip = (this.currentPage - 1) * this.pageSize;
    
    this.venueService.getAll({ skip, limit: this.pageSize }).subscribe({
      next: (response) => {
        this.venues = response.items;
        this.totalVenues = response.total;
        this.applyFilters();
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load venues';
        this.loading = false;
        console.error('Error loading venues:', err);
      }
    });
  }

  applyFilters(): void {
    this.filteredVenues = this.venues.filter(venue => {
      const matchesSearch = !this.searchTerm || 
        venue.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        venue.city?.toLowerCase().includes(this.searchTerm.toLowerCase());
      
      const matchesCountry = !this.countryFilter || 
        venue.country_code?.toLowerCase() === this.countryFilter.toLowerCase();
      
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
    if (this.currentPage * this.pageSize < this.totalVenues) {
      this.currentPage++;
      this.loadVenues();
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadVenues();
    }
  }

  get totalPages(): number {
    return Math.ceil(this.totalVenues / this.pageSize);
  }

  get Math() {
    return Math;
  }

  getVenueInitials(venueName: string): string {
    return venueName
      .split(' ')
      .map(word => word[0])
      .join('')
      .substring(0, 2)
      .toUpperCase();
  }

  getCountryFlag(countryCode: string | undefined): string {
    if (!countryCode || countryCode.length !== 3) return '🏟️';
    
    const countryFlags: Record<string, string> = {
      'IND': '🇮🇳', 'AUS': '🇦🇺', 'ENG': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'PAK': '🇵🇰',
      'NZL': '🇳🇿', 'RSA': '🇿🇦', 'WI': '🏴', 'SRI': '🇱🇰',
      'BAN': '🇧🇩', 'AFG': '🇦🇫', 'IRE': '🇮🇪', 'ZIM': '🇿🇼'
    };
    
    return countryFlags[countryCode.toUpperCase()] || '🏟️';
  }
}
