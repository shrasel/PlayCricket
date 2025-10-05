# PlayCricket Platform - Complete Development Plan

## 🎯 Project Overview
Building a high-performance Cricinfo-class cricket platform with:
- **Backend**: FastAPI (Python 3.11+) with async/await for maximum throughput
- **Frontend**: Angular 17+ (standalone components, signals, RxJS)
- **Database**: PostgreSQL with optimized indexes + Redis for caching
- **Real-time**: WebSockets + Server-Sent Events for live updates
- **Testing**: TDD approach (pytest for backend, Jasmine/Karma for frontend)

---

## 📋 PHASE 1: BACKEND API DEVELOPMENT (TDD)

### Sprint 1: Foundation Setup (Week 1)
**Duration**: 3-4 days

#### Day 1-2: Project Infrastructure
```bash
# Tech Stack
- Python 3.11+ with FastAPI 0.104+
- SQLAlchemy 2.0+ (async) with Alembic
- PostgreSQL 15+ with pg_trgm for search
- Redis 7+ for caching and sessions
- pytest + pytest-asyncio for testing
- Docker Compose for local development
```

**Deliverables**:
- [x] Virtual environment setup
- [x] FastAPI app skeleton with auto-docs
- [x] PostgreSQL + Redis Docker Compose
- [x] Alembic migration system
- [x] pytest configuration with coverage
- [x] Pre-commit hooks (black, flake8, mypy)
- [x] Environment configuration (.env handling)

#### Day 3-4: Core Models & Migrations (TDD)
**Test-First Approach**:
1. Write model tests → Implement models → Run migrations → Verify
2. Test foreign key constraints → Test unique constraints → Test enums
3. Test data validation → Test relationships → Test cascades

**Models to Create**:
```python
# Core entities (11 models)
- Team, Player, TeamPlayer
- Venue, Official
- Tournament, TournamentStage, TournamentTeam
- Match, MatchTeam, MatchOfficial, MatchToss, MatchPlayer
- Innings, Delivery
- Powerplay, DLSRevision, MatchInterruption

# Advanced features (8 models)
- Commentary, DRSEvent
- LiveMatchState, BowlingSpell
- Milestone, SuperOver
- PenaltyRuns, FieldPlacement
```

**Test Coverage**:
- ✅ Model creation and validation
- ✅ Relationship integrity (FK constraints)
- ✅ Unique constraints (no duplicate players in XI)
- ✅ Check constraints (run values >= 0)
- ✅ Cascade behavior (delete match → delete deliveries)
- ✅ Enum validation (MatchStatus, ExtraType, WicketType)

---

### Sprint 2: Repository Pattern & Business Logic (Week 1-2)

#### Day 5-7: Core Repositories (TDD)
**Test-Driven Development**:

```python
# tests/repositories/test_match_repository.py
async def test_create_match_with_teams():
    """Test creating a match with both teams"""
    match = await match_repo.create_match(
        tournament_id=1,
        venue_id=1,
        team1_id=1,
        team2_id=2,
        start_time=datetime.utcnow()
    )
    assert match.public_id is not None
    assert len(match.teams) == 2

async def test_get_live_matches():
    """Test fetching all live matches"""
    matches = await match_repo.get_live_matches()
    assert all(m.status == MatchStatus.LIVE for m in matches)
    assert len(matches) > 0
```

**Repository Pattern**:
```python
# app/repositories/base.py
class BaseRepository[T]:
    async def get_by_id(id: int) -> T | None
    async def get_by_public_id(public_id: str) -> T | None
    async def create(data: dict) -> T
    async def update(id: int, data: dict) -> T
    async def delete(id: int) -> bool
    async def list(filters: dict, pagination: Pagination) -> List[T]

# Specific repositories
- MatchRepository
- InningsRepository  
- DeliveryRepository
- PlayerRepository
- TeamRepository
- TournamentRepository
```

**Performance Optimization**:
- Async SQLAlchemy queries
- Connection pooling (pgbouncer)
- Query result caching (Redis)
- Eager loading for relationships
- Index optimization verification

---

### Sprint 3: Live Scoring API (Week 2)

#### Day 8-10: Delivery Recording (TDD)
**Test First**:

```python
# tests/api/test_live_scoring.py
async def test_create_legal_delivery():
    """Test recording a legal delivery"""
    response = await client.post("/api/deliveries", json={
        "innings_public_id": "01HP...",
        "over_number": 0,
        "ball_in_over": 1,
        "is_legal_delivery": true,
        "striker_public_id": "01HP...",
        "bowler_public_id": "01HP...",
        "runs_batter": 4,
        "is_four": true
    })
    assert response.status_code == 201
    assert response.json()["data"]["runs_batter"] == 4
    
async def test_wide_delivery_doesnt_increment_ball():
    """Test that wide doesn't advance ball count"""
    # Create wide (ball 1)
    await client.post("/api/deliveries", json={
        "ball_in_over": 1,
        "is_legal_delivery": false,
        "extra_type": "WIDE",
        "runs_extras": 1
    })
    # Next legal ball should still be ball 1
    response = await client.post("/api/deliveries", json={
        "ball_in_over": 1,  # Same ball number
        "is_legal_delivery": true,
        "runs_batter": 0
    })
    assert response.status_code == 201

async def test_innings_totals_computed_correctly():
    """Test innings summary after 1 over"""
    # Create 6 deliveries
    for ball in range(1, 7):
        await create_delivery(over=0, ball=ball, runs=ball % 3)
    
    summary = await client.get("/api/innings/{id}/summary")
    assert summary.json()["total_runs"] == 9
    assert summary.json()["overs_completed"] == 1
    assert summary.json()["current_run_rate"] == 9.0
```

**API Endpoints**:
```python
POST   /api/deliveries                    # Record ball
GET    /api/matches/{id}/live             # Live match center
GET    /api/innings/{id}/summary          # Current innings state
GET    /api/matches/{id}/current-over     # Last 6 balls
PUT    /api/deliveries/{id}/correct       # Non-destructive correction
WS     /ws/matches/{id}                   # Real-time updates
```

**Business Logic**:
- Ball sequence validation
- Legal delivery count tracking
- Real-time score calculation
- Wicket validation (max 10 wickets)
- Over completion detection
- Innings completion logic

---

### Sprint 4: Scorecard & Analytics API (Week 3)

#### Day 11-13: Statistics Views (TDD)
**Test Database Views**:

```python
async def test_batting_scorecard_accuracy():
    """Test batting figures calculation"""
    # Setup: Create innings with known deliveries
    await create_test_innings_with_deliveries()
    
    scorecard = await client.get("/api/matches/{id}/scorecard")
    rohit_stats = next(b for b in scorecard["innings"][0]["batting_card"] 
                       if b["player"]["known_as"] == "Rohit Sharma")
    
    assert rohit_stats["runs_scored"] == 45
    assert rohit_stats["balls_faced"] == 32
    assert rohit_stats["strike_rate"] == 140.62
    assert rohit_stats["fours"] == 6
    assert rohit_stats["sixes"] == 1

async def test_bowling_figures_with_maidens():
    """Test bowling figures with maiden detection"""
    # Setup: Create over with 0 runs (maiden)
    await create_maiden_over(bowler_id=1, over_num=0)
    
    figures = await client.get("/api/innings/{id}/bowling")
    bumrah_stats = next(b for b in figures 
                        if b["player"]["known_as"] == "Jasprit Bumrah")
    
    assert bumrah_stats["maidens"] == 1
    assert bumrah_stats["overs_bowled"] == "4.0"
    assert bumrah_stats["economy_rate"] == 4.5

async def test_manhattan_chart_data():
    """Test Manhattan chart generation"""
    manhattan = await client.get("/api/matches/{id}/manhattan")
    
    # Verify over 1 data
    assert manhattan[0]["over_number"] == 0
    assert manhattan[0]["runs_in_over"] == 8
    assert manhattan[0]["cumulative_runs"] == 8
    assert manhattan[0]["wickets_in_over"] == 0
```

**API Endpoints**:
```python
GET /api/matches/{id}/scorecard           # Full scorecard
GET /api/matches/{id}/partnerships        # Partnership breakdown
GET /api/matches/{id}/manhattan          # Manhattan chart data
GET /api/matches/{id}/wagon-wheel        # Shot placement
GET /api/innings/{id}/bowling            # Bowling figures
GET /api/players/{id}/stats              # Player statistics
```

**View Optimization**:
- Materialized views for heavy queries
- Partial indexes on active matches
- Query result caching (15-30s TTL)
- Pagination for large datasets

---

### Sprint 5: Tournament & League API (Week 3-4)

#### Day 14-16: League Tables & NRR (TDD)
**Complex Calculation Tests**:

```python
async def test_net_run_rate_calculation():
    """Test NRR calculation accuracy"""
    # Team A: 250/8 in 50 overs, 200/10 in 45 overs against them
    # NRR = (250/50) - (200/45) = 5.0 - 4.44 = 0.56
    
    nrr = await client.get("/api/tournaments/{id}/standings")
    team_a = next(t for t in nrr["standings"] if t["team"]["name"] == "Team A")
    
    assert team_a["net_run_rate"] == 0.56

async def test_league_table_sorting():
    """Test table sorted by points then NRR"""
    standings = await client.get("/api/tournaments/{id}/standings")
    
    # Verify sort order
    for i in range(len(standings["standings"]) - 1):
        current = standings["standings"][i]
        next_team = standings["standings"][i + 1]
        
        # Higher points come first
        if current["points"] == next_team["points"]:
            # If equal points, higher NRR comes first
            assert current["net_run_rate"] >= next_team["net_run_rate"]
        else:
            assert current["points"] > next_team["points"]
```

**API Endpoints**:
```python
GET /api/tournaments/{id}/standings       # League table
GET /api/tournaments/{id}/fixtures        # Match schedule
GET /api/teams/{id}/head-to-head         # H2H records
GET /api/teams/{id}/recent-form          # Last 5 matches
```

---

### Sprint 6: Advanced Features (Week 4)

#### Day 17-19: WebSockets, DRS, Commentary
**Real-time Testing**:

```python
async def test_websocket_delivery_broadcast():
    """Test WebSocket broadcasts delivery to all clients"""
    async with websocket_connect("/ws/matches/123") as ws1:
        async with websocket_connect("/ws/matches/123") as ws2:
            # Create delivery via REST API
            await client.post("/api/deliveries", json={...})
            
            # Both clients should receive update
            msg1 = await ws1.receive_json()
            msg2 = await ws2.receive_json()
            
            assert msg1["event_type"] == "DELIVERY"
            assert msg2["event_type"] == "DELIVERY"
            assert msg1["data"]["runs_batter"] == 4

async def test_drs_event_recording():
    """Test DRS event with ball tracking"""
    response = await client.post("/api/drs-events", json={
        "delivery_public_id": "01HP...",
        "review_type": "LBW",
        "umpire_decision": "NOT_OUT",
        "drs_decision": "OVERTURNED",
        "ball_tracking_data": {
            "impact_inline": true,
            "hitting_stumps": true,
            "wickets_missing_mm": 15.5
        }
    })
    assert response.status_code == 201
```

**Performance Targets**:
- API response time: < 50ms (p95)
- WebSocket latency: < 100ms
- Database query time: < 20ms (p99)
- Throughput: 1000+ req/s per instance

---

## 📋 PHASE 2: FRONTEND DEVELOPMENT (Angular)

### Sprint 7: Angular Foundation (Week 5)

#### Day 20-22: Project Setup
```bash
# Tech Stack
- Angular 17+ (standalone components)
- Signals for reactive state
- RxJS for async operations
- NgRx Component Store (optional)
- TailwindCSS + Angular Material
- Chart.js / D3.js for visualizations
- Socket.io-client for WebSockets
```

**Project Structure**:
```
src/app/
├── core/
│   ├── services/
│   │   ├── cricket-api.service.ts
│   │   ├── websocket.service.ts
│   │   └── cache.service.ts
│   ├── interceptors/
│   │   ├── auth.interceptor.ts
│   │   └── error.interceptor.ts
│   ├── guards/
│   │   └── auth.guard.ts
│   └── interfaces/
│       └── cricket-api.interfaces.ts
├── features/
│   ├── matches/
│   │   ├── live-center/
│   │   ├── scorecard/
│   │   └── charts/
│   ├── scorer/
│   ├── series/
│   └── players/
└── shared/
    ├── components/
    ├── pipes/
    └── directives/
```

---

### Sprint 8: Core Services (Week 5-6)

#### Day 23-25: HTTP & WebSocket Services
**Testing**:

```typescript
// cricket-api.service.spec.ts
describe('CricketApiService', () => {
  it('should fetch live match center', async () => {
    const response = await service.getLiveMatchCenter('match123');
    expect(response.data.status).toBe(MatchStatus.LIVE);
    expect(response.data.current_innings).toBeDefined();
  });

  it('should handle API errors gracefully', async () => {
    spyOn(http, 'get').and.returnValue(throwError(() => new Error()));
    await expectAsync(service.getLiveMatchCenter('invalid'))
      .toBeRejectedWithError();
  });
});

// websocket.service.spec.ts
describe('WebSocketService', () => {
  it('should receive live score updates', (done) => {
    service.connect();
    service.subscribeToMatch('match123');
    
    service.onLiveScoreUpdate().subscribe(update => {
      expect(update.match_public_id).toBe('match123');
      expect(update.latest_delivery).toBeDefined();
      done();
    });
  });
});
```

**Implementation**:
- Type-safe HTTP client with DTOs
- Retry logic with exponential backoff
- Request caching (in-memory + localStorage)
- WebSocket reconnection handling
- Offline mode support

---

### Sprint 9: Live Match Center UI (Week 6-7)

#### Day 26-30: Real-time Components
**Components**:

```typescript
// live-score-widget.component.ts
@Component({
  selector: 'app-live-score-widget',
  standalone: true,
  template: `
    <div class="score-widget">
      <div class="team-score">
        {{ currentInnings().batting_team.short_name }}
        {{ currentInnings().total_runs }}/{{ currentInnings().wickets_fallen }}
        <span class="overs">({{ currentInnings().overs_completed }}.{{ currentInnings().balls_in_current_over }})</span>
      </div>
      <div class="run-rate">
        CRR: {{ currentInnings().current_run_rate | number:'1.2-2' }}
        <span *ngIf="currentInnings().required_run_rate">
          | RRR: {{ currentInnings().required_run_rate | number:'1.2-2' }}
        </span>
      </div>
      <div class="recent-balls">
        <span *ngFor="let ball of currentInnings().recent_balls" 
              [class]="getBallClass(ball)">
          {{ ball }}
        </span>
      </div>
    </div>
  `
})
export class LiveScoreWidgetComponent {
  currentInnings = signal<CurrentInnings | null>(null);
  
  constructor(private ws: WebSocketService) {
    // Subscribe to real-time updates
    this.ws.onLiveScoreUpdate().subscribe(update => {
      this.currentInnings.set(update.current_innings);
    });
  }
}
```

**Features**:
- Auto-updating scores (WebSocket + polling fallback)
- Ball-by-ball commentary
- Current partnership display
- Required run rate calculator
- Notifications for boundaries/wickets

---

### Sprint 10: Charts & Analytics (Week 7-8)

#### Day 31-35: Visualization Components
**Manhattan Chart**:

```typescript
@Component({
  selector: 'app-manhattan-chart',
  standalone: true,
  template: `
    <canvas #chartCanvas></canvas>
  `
})
export class ManhattanChartComponent implements AfterViewInit {
  @Input() data: ManhattanDataPoint[] = [];
  @ViewChild('chartCanvas') canvas!: ElementRef;
  
  ngAfterViewInit() {
    new Chart(this.canvas.nativeElement, {
      type: 'bar',
      data: {
        labels: this.data.map(d => `Over ${d.over_number + 1}`),
        datasets: [{
          label: 'Runs per over',
          data: this.data.map(d => d.runs_in_over),
          backgroundColor: 'rgba(54, 162, 235, 0.5)'
        }]
      },
      options: {
        responsive: true,
        plugins: {
          tooltip: {
            callbacks: {
              afterLabel: (context) => {
                const point = this.data[context.dataIndex];
                return `Total: ${point.cumulative_runs}, Run Rate: ${point.over_run_rate}`;
              }
            }
          }
        }
      }
    });
  }
}
```

**Wagon Wheel**:
- SVG-based field rendering
- Shot plotting with colors (dot, 1, 2, 3, 4, 6)
- Boundary detection
- Shot zone filtering

---

### Sprint 11: Tournament Hub (Week 8-9)

#### Day 36-40: League & Fixtures
**League Table Component**:

```typescript
@Component({
  selector: 'app-league-table',
  standalone: true,
  template: `
    <table class="standings-table">
      <thead>
        <tr>
          <th>Pos</th>
          <th>Team</th>
          <th>P</th>
          <th>W</th>
          <th>L</th>
          <th>NRR</th>
          <th>Pts</th>
          <th>Form</th>
        </tr>
      </thead>
      <tbody>
        <tr *ngFor="let row of standings()" 
            [class.qualified]="row.qualification_status === 'QUALIFIED'">
          <td>{{ row.position }}</td>
          <td>
            <img [src]="row.team.logo_url" class="team-logo">
            {{ row.team.name }}
          </td>
          <td>{{ row.matches_played }}</td>
          <td>{{ row.matches_won }}</td>
          <td>{{ row.matches_lost }}</td>
          <td [class.positive]="row.net_run_rate > 0">
            {{ row.net_run_rate | number:'1.3-3' }}
          </td>
          <td><strong>{{ row.points }}</strong></td>
          <td>
            <span *ngFor="let char of row.recent_form?.split('')"
                  [class]="getFormClass(char)">
              {{ char }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  `
})
export class LeagueTableComponent {
  standings = signal<LeagueTableRow[]>([]);
}
```

---

### Sprint 12: Live Scorer Admin (Week 9-10)

#### Day 41-45: Scorer Console
**Ball Entry Interface**:

```typescript
@Component({
  selector: 'app-live-scorer',
  standalone: true,
  template: `
    <div class="scorer-console">
      <div class="match-situation">
        <h3>{{ matchState().striker?.known_as }} vs {{ matchState().bowler?.known_as }}</h3>
        <p>{{ matchState().current_over }}.{{ matchState().current_ball }}</p>
      </div>
      
      <div class="ball-entry">
        <button *ngFor="let runs of [0,1,2,3,4,6]"
                (click)="recordRuns(runs)"
                [class.boundary]="runs === 4 || runs === 6">
          {{ runs }}
        </button>
        
        <button (click)="recordExtra('WIDE')">Wide</button>
        <button (click)="recordExtra('NO_BALL')">No Ball</button>
        <button (click)="recordWicket()">Wicket</button>
      </div>
      
      <div class="quick-actions">
        <button (click)="undoLastBall()">Undo</button>
        <button (click)="openCorrection()">Correct</button>
      </div>
    </div>
  `
})
export class LiveScorerComponent {
  async recordRuns(runs: number) {
    const delivery: CreateDeliveryRequest = {
      innings_public_id: this.currentInningsId(),
      over_number: this.currentOver(),
      ball_in_over: this.currentBall(),
      is_legal_delivery: true,
      striker_public_id: this.striker().public_id,
      non_striker_public_id: this.nonStriker().public_id,
      bowler_public_id: this.bowler().public_id,
      runs_batter: runs,
      runs_extras: 0,
      is_four: runs === 4,
      is_six: runs === 6
    };
    
    await this.api.createDelivery(delivery);
    this.advanceBall();
  }
}
```

---

## 🚀 PERFORMANCE OPTIMIZATION STRATEGY

### Backend Performance
```python
# Query Optimization
- Use select_in_load for relationships
- Implement query result caching (Redis)
- Add database connection pooling
- Create covering indexes for hot queries
- Use EXPLAIN ANALYZE for slow queries

# API Performance  
- Async/await for all I/O operations
- Background tasks for heavy processing
- Response compression (gzip)
- Rate limiting (per IP/user)
- CDN for static assets

# Caching Strategy
- Live matches: 5s TTL
- Scorecards: 30s TTL  
- League tables: 5 min TTL
- Player profiles: 1 hour TTL
- Historical data: No expiry
```

### Frontend Performance
```typescript
// Optimization Techniques
- OnPush change detection strategy
- Virtual scrolling for large lists
- Lazy loading for routes
- Image optimization (WebP)
- Service worker for offline support
- Debounce search inputs
- Memoize expensive calculations
- Use trackBy for ngFor
```

---

## 📊 TESTING STRATEGY

### Backend Tests
```bash
# Test Coverage Target: 90%+
- Unit tests: Models, repositories, services (pytest)
- Integration tests: API endpoints (pytest + TestClient)
- E2E tests: Full workflows (pytest + async)
- Load tests: Performance benchmarks (locust)
- Security tests: SQL injection, XSS (bandit)
```

### Frontend Tests
```bash
# Test Coverage Target: 85%+
- Unit tests: Services, pipes, utilities (Jasmine)
- Component tests: Isolated component logic (Angular Testing)
- Integration tests: Component interactions (TestBed)
- E2E tests: User flows (Playwright/Cypress)
```

---

## 🎯 SUCCESS METRICS

### Performance KPIs
- API Response Time: < 50ms (p95), < 100ms (p99)
- WebSocket Latency: < 100ms
- Page Load Time: < 2s (First Contentful Paint)
- Time to Interactive: < 3s
- Database Query Time: < 20ms (p99)
- Test Coverage: Backend 90%+, Frontend 85%+

### Scalability
- Support 10,000+ concurrent users
- Handle 1,000+ deliveries per second
- 99.9% uptime SLA
- Horizontal scaling ready (stateless API)

---

## 📅 TIMELINE SUMMARY

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Sprint 1-2 | Week 1-2 | Backend foundation, models, repositories |
| Sprint 3-4 | Week 2-3 | Live scoring API, scorecard views |
| Sprint 5-6 | Week 3-4 | Tournament API, WebSockets, advanced features |
| Sprint 7-8 | Week 5-6 | Angular setup, core services |
| Sprint 9-10 | Week 6-8 | Live UI, charts, analytics |
| Sprint 11-12 | Week 8-10 | Tournament hub, scorer console |
| **Total** | **10 weeks** | **Full-stack production-ready platform** |

---

Let's start with **Sprint 1: Backend Foundation**! 🚀