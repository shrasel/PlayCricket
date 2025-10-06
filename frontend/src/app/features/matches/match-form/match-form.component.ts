import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, FormArray, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatchService } from '@core/services/match.service';
import { TeamService } from '@core/services/team.service';
import { VenueService } from '@core/services/venue.service';
import { TournamentService } from '@core/services/tournament.service';
import { Match, MatchCreate, MatchUpdate, MatchType, MatchStatus, Team, Venue, Tournament } from '@core/models';

@Component({
  selector: 'app-match-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './match-form.component.html',
  styleUrl: './match-form.component.scss'
})
export class MatchFormComponent implements OnInit {
  matchForm: FormGroup;
  isEditMode = false;
  matchId: string | null = null;
  loading = false;
  loadingData = false;
  error: string | null = null;
  successMessage: string | null = null;

  // Dropdowns data
  teams: Team[] = [];
  venues: Venue[] = [];
  tournaments: Tournament[] = [];

  // Enums for dropdowns
  MatchType = MatchType;
  MatchStatus = MatchStatus;
  matchTypeOptions = Object.values(MatchType);
  matchStatusOptions = Object.values(MatchStatus);

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private route: ActivatedRoute,
    private matchService: MatchService,
    private teamService: TeamService,
    private venueService: VenueService,
    private tournamentService: TournamentService
  ) {
    this.matchForm = this.createForm();
  }

  ngOnInit(): void {
    this.loadDropdownData();
    
    // Check if editing
    this.route.params.subscribe(params => {
      if (params['id']) {
        this.isEditMode = true;
        this.matchId = params['id'];
        if (this.matchId) {
          this.loadMatch(this.matchId);
        }
      }
    });
  }

  createForm(): FormGroup {
    return this.fb.group({
      venue_id: ['', Validators.required],
      tournament_id: [''],
      match_number: [''],
      match_type: [MatchType.T20, Validators.required],
      status: [MatchStatus.SCHEDULED],
      scheduled_start: [''],
      overs_per_innings: [20, [Validators.min(1)]],
      is_day_night: [false],
      is_neutral_venue: [false],
      team1_id: ['', Validators.required],
      team1_is_home: [true],
      team2_id: ['', Validators.required],
      team2_is_home: [false],
      // Toss (optional)
      include_toss: [false],
      toss_winner_id: [''],
      toss_elected_to: ['BAT']
    });
  }

  loadDropdownData(): void {
    this.loadingData = true;

    // Load teams
    this.teamService.getAll({ limit: 100 }).subscribe({
      next: (response) => {
        this.teams = response.items;
      },
      error: (err) => console.error('Error loading teams:', err)
    });

    // Load venues
    this.venueService.getAll({ limit: 100 }).subscribe({
      next: (response) => {
        this.venues = response.items;
      },
      error: (err) => console.error('Error loading venues:', err)
    });

    // Load tournaments
    this.tournamentService.getAll({ limit: 100 }).subscribe({
      next: (response) => {
        this.tournaments = response.items;
        this.loadingData = false;
      },
      error: (err) => {
        console.error('Error loading tournaments:', err);
        this.loadingData = false;
      }
    });
  }

  loadMatch(id: string): void {
    this.loading = true;
    this.matchService.getById(id).subscribe({
      next: (match: Match) => {
        this.patchFormWithMatch(match);
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load match details';
        console.error('Error loading match:', err);
        this.loading = false;
      }
    });
  }

  patchFormWithMatch(match: Match): void {
    this.matchForm.patchValue({
      venue_id: match.venue_id,
      tournament_id: match.tournament_id || '',
      match_number: match.match_number || '',
      match_type: match.match_type,
      status: match.status,
      scheduled_start: match.scheduled_start ? this.formatDateForInput(match.scheduled_start) : '',
      overs_per_innings: match.overs_per_innings || 20,
      is_day_night: match.is_day_night,
      is_neutral_venue: match.is_neutral_venue
    });

    // Set teams if available
    if (match.teams && match.teams.length >= 2) {
      this.matchForm.patchValue({
        team1_id: match.teams[0].public_id,
        team2_id: match.teams[1].public_id
      });
    }
  }

  formatDateForInput(dateString: string): string {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  }

  onMatchTypeChange(event: any): void {
    const matchType = event.target.value as MatchType;
    
    // Set default overs based on match type
    switch (matchType) {
      case MatchType.T20:
        this.matchForm.patchValue({ overs_per_innings: 20 });
        break;
      case MatchType.T10:
        this.matchForm.patchValue({ overs_per_innings: 10 });
        break;
      case MatchType.ODI:
        this.matchForm.patchValue({ overs_per_innings: 50 });
        break;
      case MatchType.THE_HUNDRED:
        this.matchForm.patchValue({ overs_per_innings: 20 });
        break;
      case MatchType.TEST:
        this.matchForm.patchValue({ overs_per_innings: null });
        break;
    }
  }

  onSubmit(): void {
    if (this.matchForm.invalid) {
      this.markFormGroupTouched(this.matchForm);
      this.error = 'Please fill in all required fields';
      return;
    }

    this.loading = true;
    this.error = null;
    this.successMessage = null;

    const formValue = this.matchForm.value;

    // Prepare match data
    if (this.isEditMode && this.matchId) {
      this.updateMatch(formValue);
    } else {
      this.createMatch(formValue);
    }
  }

  createMatch(formValue: any): void {
    const matchData: MatchCreate = {
      venue_id: formValue.venue_id,
      tournament_id: formValue.tournament_id || undefined,
      match_number: formValue.match_number || undefined,
      match_type: formValue.match_type,
      status: formValue.status,
      scheduled_start: formValue.scheduled_start ? new Date(formValue.scheduled_start).toISOString() : undefined,
      overs_per_innings: formValue.overs_per_innings || undefined,
      is_day_night: formValue.is_day_night || false,
      is_neutral_venue: formValue.is_neutral_venue || false,
      teams: [
        { team_id: formValue.team1_id, is_home: formValue.team1_is_home },
        { team_id: formValue.team2_id, is_home: formValue.team2_is_home }
      ]
    };

    // Add toss if included
    if (formValue.include_toss && formValue.toss_winner_id && formValue.toss_elected_to) {
      matchData.toss = {
        toss_winner_id: formValue.toss_winner_id,
        elected_to: formValue.toss_elected_to
      };
    }

    this.matchService.create(matchData).subscribe({
      next: (match: Match) => {
        this.successMessage = 'Match created successfully!';
        this.loading = false;
        setTimeout(() => {
          this.router.navigate(['/matches', match.public_id]);
        }, 1500);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to create match. Please try again.';
        console.error('Error creating match:', err);
        this.loading = false;
      }
    });
  }

  updateMatch(formValue: any): void {
    const updateData: MatchUpdate = {
      venue_id: formValue.venue_id,
      tournament_id: formValue.tournament_id || undefined,
      match_number: formValue.match_number || undefined,
      match_type: formValue.match_type,
      status: formValue.status,
      scheduled_start: formValue.scheduled_start ? new Date(formValue.scheduled_start).toISOString() : undefined,
      overs_per_innings: formValue.overs_per_innings || undefined,
      is_day_night: formValue.is_day_night || false,
      is_neutral_venue: formValue.is_neutral_venue || false
    };

    this.matchService.update(this.matchId!, updateData).subscribe({
      next: (match: Match) => {
        this.successMessage = 'Match updated successfully!';
        this.loading = false;
        setTimeout(() => {
          this.router.navigate(['/matches', match.public_id]);
        }, 1500);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to update match. Please try again.';
        console.error('Error updating match:', err);
        this.loading = false;
      }
    });
  }

  markFormGroupTouched(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();

      if (control instanceof FormGroup) {
        this.markFormGroupTouched(control);
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/matches']);
  }

  get Math() {
    return Math;
  }
}
