import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { PlayerService } from '../../../core/services/player.service';
import { PlayerCreate, PlayerUpdate } from '../../../core/models';

@Component({
  selector: 'app-player-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './player-form.component.html',
  styleUrl: './player-form.component.scss'
})
export class PlayerFormComponent implements OnInit {
  playerForm: FormGroup;
  isEditMode = false;
  playerId: string | null = null;
  loading = false;
  error: string | null = null;

  constructor(
    private fb: FormBuilder,
    private playerService: PlayerService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.playerForm = this.fb.group({
      full_name: ['', [Validators.required, Validators.maxLength(100)]],
      known_as: ['', [Validators.maxLength(100)]],
      dob: [''],
      batting_style: [''],
      bowling_style: ['', [Validators.maxLength(50)]]
    });
  }

  ngOnInit(): void {
    this.playerId = this.route.snapshot.paramMap.get('id');
    this.isEditMode = !!this.playerId;

    if (this.isEditMode && this.playerId) {
      this.loadPlayer(this.playerId);
    }
  }

  loadPlayer(id: string): void {
    this.loading = true;
    this.playerService.getById(id).subscribe({
      next: (player) => {
        this.playerForm.patchValue({
          full_name: player.full_name,
          known_as: player.known_as || '',
          dob: player.dob || '',
          batting_style: player.batting_style || '',
          bowling_style: player.bowling_style || ''
        });
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load player';
        this.loading = false;
        console.error('Error loading player:', err);
      }
    });
  }

  onSubmit(): void {
    if (this.playerForm.valid) {
      this.loading = true;
      this.error = null;

      const formValue = this.playerForm.value;
      const playerData: PlayerCreate | PlayerUpdate = {
        full_name: formValue.full_name,
        known_as: formValue.known_as || undefined,
        dob: formValue.dob || undefined,
        batting_style: formValue.batting_style || undefined,
        bowling_style: formValue.bowling_style || undefined
      };

      const request = this.isEditMode && this.playerId
        ? this.playerService.update(this.playerId, playerData as PlayerUpdate)
        : this.playerService.create(playerData as PlayerCreate);

      request.subscribe({
        next: (player) => {
          this.loading = false;
          this.router.navigate(['/players', player.public_id]);
        },
        error: (err) => {
          this.error = err.error?.detail || 'Failed to save player';
          this.loading = false;
          console.error('Error saving player:', err);
        }
      });
    }
  }

  onCancel(): void {
    if (this.isEditMode && this.playerId) {
      this.router.navigate(['/players', this.playerId]);
    } else {
      this.router.navigate(['/players']);
    }
  }
}
