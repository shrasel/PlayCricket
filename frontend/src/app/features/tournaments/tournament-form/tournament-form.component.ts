import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { TournamentService } from '../../../core/services/tournament.service';
import { TournamentCreate, TournamentUpdate } from '../../../core/models';

@Component({
  selector: 'app-tournament-form',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './tournament-form.component.html',
  styleUrl: './tournament-form.component.scss'
})
export class TournamentFormComponent implements OnInit {
  tournamentForm: FormGroup;
  isEditMode = false;
  tournamentId: string | null = null;
  loading = false;
  error: string | null = null;
  submitted = false;

  matchTypes = ['Test', 'ODI', 'T20', 'T10', 'T20I', 'First Class', 'List A'];
  currentYear = new Date().getFullYear();
  seasons = Array.from({ length: 10 }, (_, i) => (this.currentYear - i).toString());

  constructor(
    private fb: FormBuilder,
    private tournamentService: TournamentService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.tournamentForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(200)]],
      short_name: ['', [Validators.maxLength(50)]],
      season: [''],
      match_type: [''],
      start_date: [''],
      end_date: [''],
      points_system: ['']
    });
  }

  ngOnInit(): void {
    this.tournamentId = this.route.snapshot.paramMap.get('id');
    if (this.tournamentId) {
      this.isEditMode = true;
      this.loadTournament();
    }
  }

  loadTournament(): void {
    if (!this.tournamentId) return;

    this.loading = true;
    this.error = null;

    this.tournamentService.getById(this.tournamentId).subscribe({
      next: (tournament) => {
        this.tournamentForm.patchValue({
          name: tournament.name,
          short_name: tournament.short_name || '',
          season: tournament.season || '',
          match_type: tournament.match_type || '',
          start_date: tournament.start_date ? this.formatDateForInput(tournament.start_date) : '',
          end_date: tournament.end_date ? this.formatDateForInput(tournament.end_date) : '',
          points_system: tournament.points_system ? JSON.stringify(tournament.points_system, null, 2) : ''
        });
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load tournament';
        this.loading = false;
        console.error('Error loading tournament:', err);
      }
    });
  }

  formatDateForInput(dateString: string): string {
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
  }

  onSubmit(): void {
    this.submitted = true;

    if (this.tournamentForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = null;

    const formValue = this.tournamentForm.value;
    
    // Parse points_system JSON if provided
    let pointsSystem = null;
    if (formValue.points_system) {
      try {
        pointsSystem = JSON.parse(formValue.points_system);
      } catch (e) {
        this.error = 'Invalid JSON format for points system';
        this.loading = false;
        return;
      }
    }

    const tournamentData = {
      name: formValue.name,
      short_name: formValue.short_name || undefined,
      season: formValue.season || undefined,
      match_type: formValue.match_type || undefined,
      start_date: formValue.start_date || undefined,
      end_date: formValue.end_date || undefined,
      points_system: pointsSystem
    };

    if (this.isEditMode && this.tournamentId) {
      this.updateTournament(tournamentData as TournamentUpdate);
    } else {
      this.createTournament(tournamentData as TournamentCreate);
    }
  }

  createTournament(tournamentData: TournamentCreate): void {
    this.tournamentService.create(tournamentData).subscribe({
      next: (tournament) => {
        this.router.navigate(['/tournaments', tournament.id]);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to create tournament';
        this.loading = false;
        console.error('Error creating tournament:', err);
      }
    });
  }

  updateTournament(tournamentData: TournamentUpdate): void {
    if (!this.tournamentId) return;

    this.tournamentService.update(this.tournamentId, tournamentData).subscribe({
      next: (tournament) => {
        this.router.navigate(['/tournaments', tournament.id]);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to update tournament';
        this.loading = false;
        console.error('Error updating tournament:', err);
      }
    });
  }

  onCancel(): void {
    if (this.isEditMode && this.tournamentId) {
      this.router.navigate(['/tournaments', this.tournamentId]);
    } else {
      this.router.navigate(['/tournaments']);
    }
  }

  get f() {
    return this.tournamentForm.controls;
  }
}
