# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack application with:
- **Frontend**: React-based admin dashboard template built with Vite, Material-UI (MUI), and JWT authentication
- **Backend**: FastAPI Python backend with PostgreSQL, MongoDB, and Redis

## Development Commands

### Frontend (React + Vite)
Navigate to `frontend/` directory first:

```bash
cd frontend
npm install          # Install dependencies
npm run start        # Start dev server (runs on port 3000)
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run lint:fix     # Auto-fix ESLint issues
npm run prettier     # Format code with Prettier
```

### Backend (FastAPI)
Navigate to `backend/` directory first:

```bash
cd backend
pip install -r requirements.txt    # Install dependencies
uvicorn app.main:app --reload     # Start dev server (runs on port 8000)
alembic upgrade head               # Run database migrations
python scripts/seed_test_user.py  # Seed test user
```

### Docker Compose
Start all services from the root directory:

```bash
docker-compose up -d               # Start all services
docker-compose ps                  # Check service status
docker-compose logs backend        # View backend logs
docker-compose --profile frontend up  # Include frontend in Docker
```

**Note**: Always work within either `frontend/` or `backend/` directory for npm/pip commands.

## Architecture & Code Organization

### Authentication System

The app supports **5 authentication providers** (configured in `src/App.jsx`):
- **JWT** (default) - configured in `src/contexts/JWTContext.jsx`
- Firebase - `src/contexts/FirebaseContext.jsx`
- Auth0 - `src/contexts/Auth0Context.jsx`
- AWS Cognito - `src/contexts/AWSCognitoContext.jsx`
- Supabase - `src/contexts/SupabaseContext.jsx`

To switch providers:
1. Update `APP_AUTH` in `src/config.js`
2. Uncomment the corresponding provider import in `src/App.jsx`
3. Configure environment variables in `.env`

All auth contexts follow the same pattern with methods: `login`, `logout`, `register`, `resetPassword`, `updateProfile`.

### API Integration

- **Axios instance**: `src/utils/axios.js` - pre-configured with interceptors
- **Base URL**: Controlled by `VITE_APP_API_URL` in `.env` (defaults to mock API: https://mock-data-api-nextjs.vercel.app/)
- **API modules**: Located in `src/api/` directory (address, calendar, cart, chat, customer, invoice, kanban, menu, products, snackbar)
- **Auth token**: Stored as `serviceToken` in localStorage, automatically attached to requests via interceptor
- **401 handling**: Redirects to `/maintenance/500` on unauthorized requests

### Routing Structure

Routing uses React Router v7 with `createBrowserRouter` (configured in `src/routes/index.jsx`):

- **LoginRoutes**: Authentication pages (login, register, forgot password)
- **MainRoutes**: Protected dashboard routes (requires auth)
- **ComponentsRoutes**: UI component showcase pages
- **Simple/Landing**: Public pages with simple layout

Route definitions are split across multiple files in `src/routes/`.

### Layout System

Layouts are in `src/layout/`:
- **Dashboard**: Main authenticated layout with sidebar/header
- **Component**: For component showcase pages
- **Simple**: Minimal layout for landing/auth pages
- **Auth**: Specialized layout for authentication flows
- **Pages**: Layout for content pages

Layout type is controlled by:
- `SimpleLayoutType` enum in `src/config.js`
- `MenuOrientation` (VERTICAL/HORIZONTAL) in config

### Theme System

Theme configuration (`src/themes/`):
- **ThemeCustomization** component wraps entire app
- Supports **light/dark mode** (`ThemeMode` in config)
- **RTL support** via `ThemeDirection` (LTR/RTL)
- **Preset colors**: Configurable color schemes
- **Custom breakpoints**: xs(0), sm(768), md(1024), lg(1266), xl(1440)
- **Font families**: Inter, Poppins, Public Sans, Roboto (loaded via @fontsource)

Theme config is managed via:
- `src/config.js` - default settings
- `useConfig` hook - access/modify theme settings
- Context API for state management

### Menu System

Menu structure (`src/menu-items/`):
- Menu items are organized by category (applications, widget, forms-tables, charts-map, pages, other)
- Each category is a separate module imported in `src/menu-items/index.jsx`
- Menu supports both vertical and horizontal orientations
- Navigation drawer width: 260px (expanded), 60px (mini)

### State Management

- **Context API**: Primary state management (auth, theme, config)
- **SWR**: Data fetching and caching
- **@tanstack/react-query**: Alternative data fetching (in full-version)
- **Local state**: React hooks (useState, useReducer)

### Key Directories (src/)

```
api/          - API service modules (REST endpoints)
assets/       - Static assets (images, fonts, icons)
components/   - Reusable UI components
contexts/     - React Context providers (auth, config)
data/         - Static/mock data
hooks/        - Custom React hooks
layout/       - Page layout components
menu-items/   - Navigation menu configuration
pages/        - Page components mapped to routes
routes/       - Route definitions
sections/     - Page-specific component sections
themes/       - MUI theme configuration & overrides
utils/        - Utility functions and helpers
```

### Environment Variables

Key variables in `.env`:
- `VITE_APP_VERSION` - App version
- `VITE_APP_BASE_NAME` - Base URL path (default: `/`)
- `VITE_APP_API_URL` - Backend API endpoint
- Authentication provider keys (Firebase, Auth0, AWS, Supabase)
- `VITE_APP_GOOGLE_MAPS_API_KEY` - Google Maps integration
- `VITE_APP_MAPBOX_ACCESS_TOKEN` - Mapbox integration

### Vite Configuration

Key settings in `vite.config.mjs`:
- **Port**: 3000 (dev server)
- **JSConfig paths**: Enabled via `vite-jsconfig-paths` plugin
- **Auto-open browser**: Enabled
- **Production optimizations**: Console/debugger statements removed, code splitting by type
- **Chunk size limit**: 1000kb
- **Source maps**: Enabled in build

### Import Path Aliases

Configured in `jsconfig.json` for cleaner imports:
- Import from `components/`, `utils/`, `contexts/`, etc. without relative paths
- Example: `import useConfig from 'hooks/useConfig'` instead of `'../../../hooks/useConfig'`

## Important Development Notes

1. **Work in the correct directory**: Always `cd` into `frontend/` or `backend/` before running npm/pip commands
2. **Authentication**: Default is JWT using FastAPI backend at http://localhost:8000
3. **API calls**: Use the pre-configured axios instance from `frontend/src/utils/axios.js` for automatic token handling
4. **Environment Variables**:
   - Frontend: `frontend/.env` (VITE_APP_API_URL)
   - Backend: `backend/.env` (DB credentials, JWT secrets)
5. **Database**: PostgreSQL on port 5432, MongoDB on port 27017, Redis on port 6379
6. **Default Login**: Email: info@codedthemes.com, Password: 12345
7. **Theme changes**: Modify `frontend/src/config.js` or use the `useConfig` hook
8. **New routes**: Add to appropriate route file in `frontend/src/routes/` and update menu items in `frontend/src/menu-items/`
9. **Production build**: Console logs are automatically removed in production builds
