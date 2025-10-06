import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { VenueService } from '../../../core/services/venue.service';
import { VenueCreate, VenueUpdate } from '../../../core/models';

@Component({
  selector: 'app-venue-form',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './venue-form.component.html',
  styleUrl: './venue-form.component.scss'
})
export class VenueFormComponent implements OnInit {
  venueForm: FormGroup;
  isEditMode = false;
  venueId: string | null = null;
  loading = false;
  error: string | null = null;
  submitted = false;

  constructor(
    private fb: FormBuilder,
    private venueService: VenueService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.venueForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(200)]],
      city: ['', [Validators.maxLength(100)]],
      country_code: ['', [Validators.maxLength(3)]],
      timezone_name: ['', [Validators.maxLength(64)]],
      ends_names: ['', [Validators.maxLength(200)]]
    });
  }

  ngOnInit(): void {
    this.venueId = this.route.snapshot.paramMap.get('id');
    if (this.venueId) {
      this.isEditMode = true;
      this.loadVenue();
    }
  }

  loadVenue(): void {
    if (!this.venueId) return;

    this.loading = true;
    this.venueService.getById(this.venueId).subscribe({
      next: (venue) => {
        this.venueForm.patchValue({
          name: venue.name,
          city: venue.city || '',
          country_code: venue.country_code || '',
          timezone_name: venue.timezone_name || '',
          ends_names: venue.ends_names || ''
        });
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load venue';
        this.loading = false;
        console.error('Error loading venue:', err);
      }
    });
  }

  onSubmit(): void {
    this.submitted = true;
    
    if (this.venueForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = null;

    const formValue = this.venueForm.value;
    
    // Remove empty optional fields
    const venueData: any = {
      name: formValue.name
    };

    if (formValue.city) venueData.city = formValue.city;
    if (formValue.country_code) venueData.country_code = formValue.country_code;
    if (formValue.timezone_name) venueData.timezone_name = formValue.timezone_name;
    if (formValue.ends_names) venueData.ends_names = formValue.ends_names;

    const request = this.isEditMode && this.venueId
      ? this.venueService.update(this.venueId, venueData as VenueUpdate)
      : this.venueService.create(venueData as VenueCreate);

    request.subscribe({
      next: (venue) => {
        this.router.navigate(['/venues', venue.public_id]);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to save venue';
        this.loading = false;
        console.error('Error saving venue:', err);
      }
    });
  }

  onCancel(): void {
    if (this.isEditMode && this.venueId) {
      this.router.navigate(['/venues', this.venueId]);
    } else {
      this.router.navigate(['/venues']);
    }
  }

  get f() {
    return this.venueForm.controls;
  }
}
