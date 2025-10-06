import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Match, Player } from '../../../core/models';

interface MatchSetup {
  tossWinnerId?: number;
  tossDecision?: 'BAT' | 'BOWL';
  team1Players: Player[];
  team2Players: Player[];
  team1Lineup: number[];
  team2Lineup: number[];
  battingTeamId?: number;
  bowlingTeamId?: number;
}

@Component({
  selector: 'app-team-lineup',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './team-lineup.component.html',
  styleUrls: ['./team-lineup.component.scss']
})
export class TeamLineupComponent implements OnInit {
  @Input() match!: Match;
  @Input() matchSetup!: MatchSetup;
  @Input() allPlayers!: Player[];
  
  @Output() lineupComplete = new EventEmitter<{
    team1Lineup: number[];
    team2Lineup: number[];
  }>();
  @Output() back = new EventEmitter<void>();

  activeTab: 'team1' | 'team2' = 'team1';
  
  team1SelectedPlayers: Player[] = [];
  team2SelectedPlayers: Player[] = [];
  
  team1Captain?: number;
  team2Captain?: number;
  
  team1ViceCaptain?: number;
  team2ViceCaptain?: number;
  
  searchTerm1 = '';
  searchTerm2 = '';

  ngOnInit(): void {
    // Determine which tab to show first based on batting team
    if (this.matchSetup.battingTeamId === this.getTeamId(1)) {
      this.activeTab = 'team2';
    }
  }

  getTeamId(index: number): number {
    const publicId = this.match.teams?.[index]?.public_id;
    return publicId ? parseInt(publicId) : 0;
  }

  getTeamName(index: number): string {
    return this.match.teams?.[index]?.name || `Team ${index + 1}`;
  }

  getTeamPlayers(teamIndex: number): Player[] {
    const teamId = this.getTeamId(teamIndex);
    return teamIndex === 0 ? this.matchSetup.team1Players : this.matchSetup.team2Players;
  }

  getFilteredPlayers(teamIndex: number): Player[] {
    const players = this.getTeamPlayers(teamIndex);
    const searchTerm = teamIndex === 0 ? this.searchTerm1 : this.searchTerm2;
    
    if (!searchTerm.trim()) {
      return players;
    }

    return players.filter(player =>
      player.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      player.known_as?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      player.batting_style?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      player.bowling_style?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }

  getSelectedPlayers(teamIndex: number): Player[] {
    return teamIndex === 0 ? this.team1SelectedPlayers : this.team2SelectedPlayers;
  }

  isPlayerSelected(player: Player, teamIndex: number): boolean {
    const selected = this.getSelectedPlayers(teamIndex);
    return selected.some(p => p.id === player.id);
  }

  canSelectMore(teamIndex: number): boolean {
    return this.getSelectedPlayers(teamIndex).length < 11;
  }

  togglePlayerSelection(player: Player, teamIndex: number): void {
    const selected = this.getSelectedPlayers(teamIndex);
    const isSelected = this.isPlayerSelected(player, teamIndex);

    if (isSelected) {
      // Remove player
      const updatedSelection = selected.filter(p => p.id !== player.id);
      if (teamIndex === 0) {
        this.team1SelectedPlayers = updatedSelection;
        // Clear captain/vice-captain if they were deselected
        if (this.team1Captain === player.id) this.team1Captain = undefined;
        if (this.team1ViceCaptain === player.id) this.team1ViceCaptain = undefined;
      } else {
        this.team2SelectedPlayers = updatedSelection;
        if (this.team2Captain === player.id) this.team2Captain = undefined;
        if (this.team2ViceCaptain === player.id) this.team2ViceCaptain = undefined;
      }
    } else if (this.canSelectMore(teamIndex)) {
      // Add player
      if (teamIndex === 0) {
        this.team1SelectedPlayers = [...selected, player];
      } else {
        this.team2SelectedPlayers = [...selected, player];
      }
    }
  }

  movePlayerUp(player: Player, teamIndex: number): void {
    const selected = this.getSelectedPlayers(teamIndex);
    const index = selected.findIndex(p => p.id === player.id);
    
    if (index > 0) {
      const newSelection = [...selected];
      [newSelection[index - 1], newSelection[index]] = [newSelection[index], newSelection[index - 1]];
      
      if (teamIndex === 0) {
        this.team1SelectedPlayers = newSelection;
      } else {
        this.team2SelectedPlayers = newSelection;
      }
    }
  }

  movePlayerDown(player: Player, teamIndex: number): void {
    const selected = this.getSelectedPlayers(teamIndex);
    const index = selected.findIndex(p => p.id === player.id);
    
    if (index < selected.length - 1) {
      const newSelection = [...selected];
      [newSelection[index], newSelection[index + 1]] = [newSelection[index + 1], newSelection[index]];
      
      if (teamIndex === 0) {
        this.team1SelectedPlayers = newSelection;
      } else {
        this.team2SelectedPlayers = newSelection;
      }
    }
  }

  setCaptain(playerId: number, teamIndex: number): void {
    if (teamIndex === 0) {
      this.team1Captain = this.team1Captain === playerId ? undefined : playerId;
    } else {
      this.team2Captain = this.team2Captain === playerId ? undefined : playerId;
    }
  }

  setViceCaptain(playerId: number, teamIndex: number): void {
    if (teamIndex === 0) {
      this.team1ViceCaptain = this.team1ViceCaptain === playerId ? undefined : playerId;
    } else {
      this.team2ViceCaptain = this.team2ViceCaptain === playerId ? undefined : playerId;
    }
  }

  getCaptain(teamIndex: number): number | undefined {
    return teamIndex === 0 ? this.team1Captain : this.team2Captain;
  }

  getViceCaptain(teamIndex: number): number | undefined {
    return teamIndex === 0 ? this.team1ViceCaptain : this.team2ViceCaptain;
  }

  isTeamValid(teamIndex: number): boolean {
    const selected = this.getSelectedPlayers(teamIndex);
    const captain = this.getCaptain(teamIndex);
    return selected.length === 11 && captain !== undefined;
  }

  get isValid(): boolean {
    return this.isTeamValid(0) && this.isTeamValid(1);
  }

  getPlayerRole(player: Player): string {
    const hasBatting = player.batting_style && player.batting_style !== 'NONE';
    const hasBowling = player.bowling_style && player.bowling_style !== 'NONE';

    if (hasBatting && hasBowling) {
      return 'All-rounder';
    } else if (hasBatting) {
      return 'Batsman';
    } else if (hasBowling) {
      return 'Bowler';
    }
    return 'Player';
  }

  submitLineup(): void {
    if (this.isValid) {
      this.lineupComplete.emit({
        team1Lineup: this.team1SelectedPlayers.map(p => p.id),
        team2Lineup: this.team2SelectedPlayers.map(p => p.id)
      });
    }
  }

  goBack(): void {
    this.back.emit();
  }
}
