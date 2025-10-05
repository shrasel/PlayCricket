# PlayCricket Frontend

A comprehensive Angular 18 web application for live cricket scoring, statistics, and match management.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
cd frontend
npm install
npm start
```

The app will be available at http://localhost:4200

## 📁 Project Structure

```
src/
├── app/
│   ├── core/                 # Core services, interceptors, guards
│   │   ├── interceptors/     # HTTP interceptors
│   │   ├── models/           # TypeScript interfaces
│   │   └── services/         # API services
│   ├── features/             # Feature modules
│   │   ├── dashboard/        # Home dashboard
│   │   ├── teams/            # Team management
│   │   ├── players/          # Player management
│   │   ├── venues/           # Venue management
│   │   ├── tournaments/      # Tournament management
│   │   ├── matches/          # Match management
│   │   ├── live-scoring/     # Ball-by-ball scoring
│   │   └── statistics/       # Stats & analytics
│   ├── shared/               # Shared components & utilities
│   │   ├── components/       # Reusable components
│   │   └── pipes/            # Custom pipes
│   ├── app.component.ts      # Root component
│   ├── app.config.ts         # App configuration
│   └── app.routes.ts         # Route definitions
├── environments/             # Environment configs
└── styles.scss               # Global styles
```

## ✨ Features

### 🏏 Cricket Management
- **Teams**: Create, edit, search teams by country
- **Players**: Manage players with filters (age, style)
- **Venues**: Track venues with location details
- **Tournaments**: Organize tournaments with brackets

### 📊 Live Scoring
- Ball-by-ball scoring interface
- Real-time scorecard updates
- Current partnership tracking
- Over summaries with commentary
- Support for all delivery types (runs, wickets, extras)

### 📈 Statistics & Analytics
- Full match scorecards
- Batsman statistics (runs, SR, 4s, 6s)
- Bowler statistics (wickets, economy, overs)
- Career aggregates across matches
- Wagon wheel visualization
- Pitch map visualization

### 🎨 Modern UI/UX
- Tailwind CSS styling
- Cricket-themed color palette
- Dark mode support
- Fully responsive design
- Loading states & skeletons
- Error handling & notifications

## 🛠️ Tech Stack

- **Framework**: Angular 18 (Standalone Components)
- **Styling**: Tailwind CSS 3.4
- **State Management**: RxJS
- **HTTP Client**: Angular HttpClient with Interceptors
- **Routing**: Angular Router with lazy loading
- **TypeScript**: 5.5+ with strict mode

## 📡 API Integration

All API calls go through dedicated services:
- `TeamService` - Team CRUD operations
- `PlayerService` - Player management
- `VenueService` - Venue operations
- `TournamentService` - Tournament management
- `MatchService` - Match orchestration
- `InningsService` - Innings tracking
- `DeliveryService` - Ball-by-ball scoring
- `StatisticsService` - Analytics & stats

## 🔐 HTTP Interceptors

1. **Auth Interceptor**: Adds authentication tokens
2. **Error Interceptor**: Global error handling
3. **Loading Interceptor**: Manages loading states

## 🎯 Key Components

### Dashboard
- Live matches display
- Upcoming matches
- Recent results
- Quick stats

### Live Scoring Interface
- Delivery input form
- Real-time scorecard
- Partnership tracker
- Over summary
- Wagon wheel & pitch map

### Match Management
- Create match wizard
- Toss management
- Status controls (SCHEDULED → LIVE → COMPLETED)
- Result recording

## 🚢 Build & Deploy

### Development
```bash
npm start              # Start dev server
npm run watch          # Build with watch mode
```

### Production
```bash
npm run build          # Build for production
```

Output will be in `dist/playcricket-frontend/`

### Docker
```bash
docker build -t playcricket-frontend .
docker run -p 80:80 playcricket-frontend
```

## 🧪 Testing

```bash
npm test               # Run unit tests
npm run test:coverage  # Run with coverage
```

## 📝 Code Style

- ESLint for linting
- Prettier for formatting
- Strict TypeScript mode
- Standalone components only

## 🌐 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📄 License

MIT

## 👥 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 🐛 Known Issues

None currently

## 🗺️ Roadmap

- [ ] WebSocket for real-time updates
- [ ] Player photo uploads
- [ ] Match highlights
- [ ] Commentary AI
- [ ] Fantasy cricket integration
- [ ] Push notifications
- [ ] PWA support

## 📞 Support

For issues and questions, please open a GitHub issue.

---

Built with ❤️ for cricket fans worldwide 🏏
