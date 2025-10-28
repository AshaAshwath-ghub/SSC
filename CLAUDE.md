# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Mantis Material React Admin Template** - a React-based admin dashboard template built with Vite, Material-UI (MUI), and multiple authentication providers. The repository contains two versions:

- **full-version**: Complete dashboard with all features, pages, and components pre-integrated
- **seed**: Minimal setup with essential dependencies for building from scratch

## Development Commands

### Full Version
Navigate to `full-version/` directory first:

```bash
cd full-version
npm install          # Install dependencies
npm run start        # Start dev server (runs on port 3000)
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run lint:fix     # Auto-fix ESLint issues
npm run prettier     # Format code with Prettier
```

### Seed Version
Navigate to `seed/` directory first:

```bash
cd seed
npm install          # Install dependencies
npm run start        # Start dev server
npm run build        # Production build
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run lint:fix     # Auto-fix ESLint issues
npm run prettier     # Format code with Prettier
```

**Note**: Both versions use the same npm scripts. Always work within either `full-version/` or `seed/` directory, not the root.

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

1. **Work in the correct directory**: Always `cd` into `full-version/` or `seed/` before running npm commands
2. **Authentication**: Default is JWT using mock backend. Switch providers by modifying `src/App.jsx` and `src/config.js`
3. **API calls**: Use the pre-configured axios instance from `src/utils/axios.js` for automatic token handling
4. **Theme changes**: Modify `src/config.js` or use the `useConfig` hook to change theme settings dynamically
5. **New routes**: Add to appropriate route file in `src/routes/` and update menu items in `src/menu-items/`
6. **Components**: Full-version includes extensive component library (forms, tables, charts, etc.); seed has minimal components
7. **Production build**: Console logs are automatically removed in production builds
