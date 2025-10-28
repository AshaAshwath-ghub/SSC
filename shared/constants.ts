/**
 * Shared constants across frontend and backend.
 */

// ============================================================================
// API Configuration
// ============================================================================

export const API_VERSION = 'v1';
export const API_PREFIX = `/api/${API_VERSION}`;

// ============================================================================
// Authentication
// ============================================================================

export const AUTH_ENDPOINTS = {
  REGISTER: `${API_PREFIX}/auth/register`,
  LOGIN: `${API_PREFIX}/auth/login`,
  LOGOUT: `${API_PREFIX}/auth/logout`,
  REFRESH: `${API_PREFIX}/auth/refresh`,
  FORGOT_PASSWORD: `${API_PREFIX}/auth/forgot-password`,
  RESET_PASSWORD: `${API_PREFIX}/auth/reset-password`,
  VERIFY_EMAIL: `${API_PREFIX}/auth/verify-email`,

  // OAuth
  OAUTH_AUTHORIZE: (provider: string) => `${API_PREFIX}/auth/oauth/${provider}/authorize`,
  OAUTH_CALLBACK: (provider: string) => `${API_PREFIX}/auth/oauth/${provider}/callback`,
  OAUTH_LINK: `${API_PREFIX}/auth/oauth/link`,

  // MFA
  MFA_ENROLL: `${API_PREFIX}/auth/mfa/enroll`,
  MFA_VERIFY_ENROLLMENT: `${API_PREFIX}/auth/mfa/verify-enrollment`,
  MFA_VERIFY: `${API_PREFIX}/auth/mfa/verify`,
  MFA_UNENROLL: `${API_PREFIX}/auth/mfa/unenroll`,
  MFA_BACKUP_CODES: `${API_PREFIX}/auth/mfa/backup-codes`,

  // reCAPTCHA
  RECAPTCHA_VERIFY: `${API_PREFIX}/auth/recaptcha/verify`,
} as const;

// ============================================================================
// User & Preferences
// ============================================================================

export const USER_ENDPOINTS = {
  ME: `${API_PREFIX}/users/me`,
  UPDATE_PROFILE: `${API_PREFIX}/users/me`,
  CHANGE_PASSWORD: `${API_PREFIX}/users/me/password`,
  PREFERENCES: `${API_PREFIX}/users/me/preferences`,
  SESSIONS: `${API_PREFIX}/users/me/sessions`,
  PERMISSIONS: `${API_PREFIX}/users/me/permissions`,
} as const;

// ============================================================================
// Dashboard & Widgets
// ============================================================================

export const DASHBOARD_ENDPOINTS = {
  LIST: `${API_PREFIX}/dashboards`,
  CREATE: `${API_PREFIX}/dashboards`,
  GET: (id: number) => `${API_PREFIX}/dashboards/${id}`,
  UPDATE: (id: number) => `${API_PREFIX}/dashboards/${id}`,
  DELETE: (id: number) => `${API_PREFIX}/dashboards/${id}`,
  PUBLISH: (id: number) => `${API_PREFIX}/dashboards/${id}/publish`,
  PREVIEW: (id: number) => `${API_PREFIX}/dashboards/${id}/preview`,
} as const;

export const WIDGET_ENDPOINTS = {
  CREATE: `${API_PREFIX}/widgets`,
  UPDATE: (id: string) => `${API_PREFIX}/widgets/${id}`,
  DELETE: (id: string) => `${API_PREFIX}/widgets/${id}`,
  TYPES: `${API_PREFIX}/widget-types`,
  DATA: `${API_PREFIX}/widget-data`,
} as const;

// ============================================================================
// Admin Endpoints
// ============================================================================

export const ADMIN_ENDPOINTS = {
  BRANDING: `${API_PREFIX}/admin/branding`,
  PWA_CONFIG: `${API_PREFIX}/admin/pwa-config`,
  TRANSLATIONS: `${API_PREFIX}/admin/translations`,
  USERS: `${API_PREFIX}/admin/users`,
  ROLES: `${API_PREFIX}/admin/roles`,
} as const;

// ============================================================================
// System Endpoints
// ============================================================================

export const SYSTEM_ENDPOINTS = {
  HEALTH: '/health',
  READY: '/ready',
  LIVE: '/live',
} as const;

// ============================================================================
// Token Configuration
// ============================================================================

export const TOKEN_CONFIG = {
  ACCESS_TOKEN_KEY: 'access_token',
  REFRESH_TOKEN_KEY: 'refresh_token',
  TOKEN_TYPE: 'Bearer',
} as const;

// ============================================================================
// Pagination
// ============================================================================

export const PAGINATION_DEFAULTS = {
  PAGE: 1,
  PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
} as const;

// ============================================================================
// Widget Types
// ============================================================================

export const WIDGET_TYPES = {
  CHART: 'chart',
  TABLE: 'table',
  CARD: 'card',
  CALENDAR: 'calendar',
  TREE: 'tree',
} as const;

export const WIDGET_TYPE_LABELS = {
  [WIDGET_TYPES.CHART]: 'Chart/Graph',
  [WIDGET_TYPES.TABLE]: 'Data Table',
  [WIDGET_TYPES.CARD]: 'Card',
  [WIDGET_TYPES.CALENDAR]: 'Calendar',
  [WIDGET_TYPES.TREE]: 'Tree View',
} as const;

// ============================================================================
// MFA Types
// ============================================================================

export const MFA_TYPES = {
  SMS: 'sms',
  EMAIL: 'email',
  DUO: 'duo',
  TOTP: 'totp',
} as const;

export const MFA_TYPE_LABELS = {
  [MFA_TYPES.SMS]: 'SMS',
  [MFA_TYPES.EMAIL]: 'Email',
  [MFA_TYPES.DUO]: 'Duo Push',
  [MFA_TYPES.TOTP]: 'Authenticator App',
} as const;

// ============================================================================
// OAuth Providers
// ============================================================================

export const OAUTH_PROVIDERS = {
  GOOGLE: 'google',
  MICROSOFT: 'microsoft',
  FACEBOOK: 'facebook',
} as const;

export const OAUTH_PROVIDER_LABELS = {
  [OAUTH_PROVIDERS.GOOGLE]: 'Google',
  [OAUTH_PROVIDERS.MICROSOFT]: 'Microsoft',
  [OAUTH_PROVIDERS.FACEBOOK]: 'Facebook',
} as const;

// ============================================================================
// Themes
// ============================================================================

export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto',
} as const;

// ============================================================================
// Locales
// ============================================================================

export const DEFAULT_LOCALE = 'en';

export const SUPPORTED_LOCALES = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'es', name: 'Spanish', nativeName: 'Español' },
  { code: 'fr', name: 'French', nativeName: 'Français' },
  { code: 'de', name: 'German', nativeName: 'Deutsch' },
] as const;

// ============================================================================
// Status Codes
// ============================================================================

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const;

// ============================================================================
// Error Codes
// ============================================================================

export const ERROR_CODES = {
  // Authentication
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  USER_NOT_FOUND: 'USER_NOT_FOUND',
  USER_ALREADY_EXISTS: 'USER_ALREADY_EXISTS',
  INVALID_TOKEN: 'INVALID_TOKEN',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  ACCOUNT_LOCKED: 'ACCOUNT_LOCKED',
  ACCOUNT_NOT_VERIFIED: 'ACCOUNT_NOT_VERIFIED',

  // MFA
  MFA_REQUIRED: 'MFA_REQUIRED',
  INVALID_MFA_CODE: 'INVALID_MFA_CODE',
  MFA_NOT_ENROLLED: 'MFA_NOT_ENROLLED',

  // Authorization
  INSUFFICIENT_PERMISSIONS: 'INSUFFICIENT_PERMISSIONS',

  // Rate Limiting
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',

  // Validation
  VALIDATION_ERROR: 'VALIDATION_ERROR',

  // Resources
  RESOURCE_NOT_FOUND: 'RESOURCE_NOT_FOUND',
  RESOURCE_ALREADY_EXISTS: 'RESOURCE_ALREADY_EXISTS',

  // System
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
} as const;

// ============================================================================
// Grid Configuration
// ============================================================================

export const GRID_DEFAULTS = {
  COLUMNS: 12,
  ROW_HEIGHT: 60,
  MARGIN: [10, 10] as [number, number],
  CONTAINER_PADDING: [10, 10] as [number, number],
} as const;

// ============================================================================
// Date & Time Formats
// ============================================================================

export const DATE_FORMATS = {
  DATE_ONLY: 'yyyy-MM-dd',
  TIME_ONLY: 'HH:mm:ss',
  DATETIME: 'yyyy-MM-dd HH:mm:ss',
  DATETIME_WITH_TZ: "yyyy-MM-dd'T'HH:mm:ssXXX",
  DISPLAY_DATE: 'MMM d, yyyy',
  DISPLAY_DATETIME: 'MMM d, yyyy h:mm a',
} as const;

// ============================================================================
// Storage Keys
// ============================================================================

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'app_access_token',
  REFRESH_TOKEN: 'app_refresh_token',
  USER: 'app_user',
  PREFERENCES: 'app_preferences',
  THEME: 'app_theme',
  LANGUAGE: 'app_language',
} as const;
