import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { TeamService } from '../../../core/services/team.service';
import { TeamCreate, TeamUpdate } from '../../../core/models';

@Component({
  selector: 'app-team-form',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './team-form.component.html',
  styleUrl: './team-form.component.scss'
})
export class TeamFormComponent implements OnInit {
  teamForm: FormGroup;
  isEditMode = false;
  teamId: string | null = null;
  loading = false;
  error: string | null = null;
  submitted = false;

  constructor(
    private fb: FormBuilder,
    private teamService: TeamService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.teamForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(100)]],
      short_name: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(10)]],
      country_code: ['', [Validators.maxLength(3)]],
      logo_url: ['', [Validators.maxLength(500)]],
      primary_color: [''],
      secondary_color: ['']
    });
  }

  ngOnInit(): void {
    this.teamId = this.route.snapshot.paramMap.get('id');
    if (this.teamId) {
      this.isEditMode = true;
      this.loadTeam();
    }
  }

  loadTeam(): void {
    if (!this.teamId) return;

    this.loading = true;
    this.teamService.getById(this.teamId).subscribe({
      next: (team) => {
        this.teamForm.patchValue({
          name: team.name,
          short_name: team.short_name,
          country_code: team.country_code || '',
          logo_url: team.logo_url || '',
          primary_color: team.primary_color || '',
          secondary_color: team.secondary_color || ''
        });
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load team';
        this.loading = false;
        console.error('Error loading team:', err);
      }
    });
  }

  onSubmit(): void {
    this.submitted = true;
    
    if (this.teamForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = null;

    const formValue = this.teamForm.value;
    
    // Remove empty optional fields
    const teamData: any = {
      name: formValue.name,
      short_name: formValue.short_name
    };

    if (formValue.country_code) teamData.country_code = formValue.country_code;
    if (formValue.logo_url) teamData.logo_url = formValue.logo_url;
    if (formValue.primary_color) teamData.primary_color = formValue.primary_color;
    if (formValue.secondary_color) teamData.secondary_color = formValue.secondary_color;

    const request = this.isEditMode && this.teamId
      ? this.teamService.update(this.teamId, teamData as TeamUpdate)
      : this.teamService.create(teamData as TeamCreate);

    request.subscribe({
      next: (team) => {
        this.router.navigate(['/teams', team.public_id]);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to save team';
        this.loading = false;
        console.error('Error saving team:', err);
      }
    });
  }

  onCancel(): void {
    if (this.isEditMode && this.teamId) {
      this.router.navigate(['/teams', this.teamId]);
    } else {
      this.router.navigate(['/teams']);
    }
  }

  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = '';
  }

  get f() {
    return this.teamForm.controls;
  }
}
