import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, ActivatedRoute } from '@angular/router';
import { Venue } from '../../../core/models';
import { VenueService } from '../../../core/services/venue.service';

@Component({
  selector: 'app-venue-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './venue-detail.component.html',
  styleUrl: './venue-detail.component.scss'
})
export class VenueDetailComponent implements OnInit {
  venue: Venue | null = null;
  loading = false;
  error: string | null = null;
  showDeleteModal = false;
  deleting = false;

  constructor(
    private venueService: VenueService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const venueId = this.route.snapshot.paramMap.get('id');
    if (venueId) {
      this.loadVenue(venueId);
    }
  }

  loadVenue(venueId: string): void {
    this.loading = true;
    this.error = null;

    this.venueService.getById(venueId).subscribe({
      next: (venue) => {
        this.venue = venue;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load venue';
        this.loading = false;
        console.error('Error loading venue:', err);
      }
    });
  }

  onEdit(): void {
    if (this.venue) {
      this.router.navigate(['/venues', this.venue.public_id, 'edit']);
    }
  }

  onDelete(): void {
    this.showDeleteModal = true;
  }

  confirmDelete(): void {
    if (!this.venue) return;

    this.deleting = true;
    this.venueService.delete(this.venue.public_id).subscribe({
      next: () => {
        this.router.navigate(['/venues']);
      },
      error: (err) => {
        this.error = 'Failed to delete venue';
        this.deleting = false;
        this.showDeleteModal = false;
        console.error('Error deleting venue:', err);
      }
    });
  }

  cancelDelete(): void {
    this.showDeleteModal = false;
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

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}
