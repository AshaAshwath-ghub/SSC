/**
 * Shared TypeScript types for frontend and backend communication.
 * Keep these in sync with backend Pydantic schemas.
 */

// ============================================================================
// User & Authentication Types
// ============================================================================

export interface User {
  id: number;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  isActive: boolean;
  isVerified: boolean;
  isSuperuser: boolean;
  lastLogin?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AuthProvider {
  id: number;
  userId: number;
  providerType: 'google' | 'microsoft' | 'facebook' | 'firebase';
  providerUserId: string;
  providerEmail?: string;
  createdAt: string;
}

export interface LoginRequest {
  username: string;
  password: string;
  recaptchaToken?: string;
}

export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
  user: User;
  requiresMFA?: boolean;
  mfaToken?: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
  recaptchaToken?: string;
}

export interface TokenRefreshRequest {
  refreshToken: string;
}

export interface TokenRefreshResponse {
  accessToken: string;
  tokenType: string;
  expiresIn: number;
}

// ============================================================================
// MFA Types
// ============================================================================

export type MFAType = 'sms' | 'email' | 'duo' | 'totp';

export interface MFAEnrollment {
  id: number;
  userId: number;
  mfaType: MFAType;
  isActive: boolean;
  isPrimary: boolean;
  verifiedAt?: string;
  lastUsedAt?: string;
  createdAt: string;
}

export interface MFAEnrollRequest {
  mfaType: MFAType;
  identifier: string; // phone number, email, or empty for TOTP
}

export interface MFAEnrollResponse {
  enrollmentId: number;
  mfaType: MFAType;
  qrCode?: string; // For TOTP
  secret?: string; // For TOTP
  identifier?: string; // For SMS/Email
}

export interface MFAVerifyRequest {
  enrollmentId?: number;
  mfaToken?: string;
  code: string;
}

export interface MFAVerifyResponse {
  success: boolean;
  accessToken?: string;
  refreshToken?: string;
  backupCodes?: string[]; // Returned only on first verification
}

// ============================================================================
// OAuth Types
// ============================================================================

export type OAuthProvider = 'google' | 'microsoft' | 'facebook';

export interface OAuthAuthorizeRequest {
  provider: OAuthProvider;
  redirectUri?: string;
  state?: string;
}

export interface OAuthAuthorizeResponse {
  authorizationUrl: string;
  state: string;
}

export interface OAuthCallbackRequest {
  code: string;
  state: string;
}

// ============================================================================
// User Preferences Types
// ============================================================================

export interface UserPreferences {
  userId: number;
  theme: 'light' | 'dark' | 'auto';
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  dashboardSettings: {
    defaultDashboard?: string;
    refreshInterval?: number;
  };
  [key: string]: any; // Allow custom preferences
}

// ============================================================================
// Dashboard & Widget Types
// ============================================================================

export interface Dashboard {
  id: number;
  name: string;
  description?: string;
  ownerId: number;
  isPublished: boolean;
  routeSlug?: string;
  gridConfig?: GridConfig;
  themeConfig?: ThemeConfig;
  version: number;
  publishedVersion?: number;
  publishedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface GridConfig {
  columns: number;
  rowHeight: number;
  compactType?: 'vertical' | 'horizontal' | null;
  preventCollision?: boolean;
  margin?: [number, number];
  containerPadding?: [number, number];
}

export interface ThemeConfig {
  primaryColor?: string;
  backgroundColor?: string;
  textColor?: string;
  [key: string]: any;
}

export type WidgetType = 'chart' | 'table' | 'card' | 'calendar' | 'tree';

export interface Widget {
  id: string;
  dashboardId: number;
  type: WidgetType;
  title: string;
  config: WidgetConfig;
  dataSource: DataSource;
  position: WidgetPosition;
  createdAt: string;
  updatedAt: string;
}

export interface WidgetPosition {
  x: number;
  y: number;
  w: number;
  h: number;
  minW?: number;
  minH?: number;
  maxW?: number;
  maxH?: number;
}

export interface WidgetConfig {
  [key: string]: any; // Widget-specific configuration
}

export interface DataSource {
  type: 'api' | 'sql' | 'mongodb' | 'static';
  url?: string;
  query?: string;
  params?: Record<string, any>;
  refreshInterval?: number; // seconds
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ApiError;
  message?: string;
  requestId?: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface HealthCheck {
  status: 'healthy' | 'unhealthy' | 'degraded';
  version: string;
  environment: string;
  services: {
    [key: string]: ServiceHealth;
  };
}

export interface ServiceHealth {
  status: 'healthy' | 'unhealthy';
  type?: string;
  error?: string;
}

// ============================================================================
// Branding Types
// ============================================================================

export interface BrandingConfig {
  appName: string;
  appLogo?: string;
  appLogoDark?: string;
  favicon?: string;
  primaryColor?: string;
  secondaryColor?: string;
  tagline?: string;
  [key: string]: any;
}

// ============================================================================
// PWA Types
// ============================================================================

export interface PWAManifest {
  name: string;
  short_name: string;
  description?: string;
  start_url: string;
  display: 'standalone' | 'fullscreen' | 'minimal-ui' | 'browser';
  background_color: string;
  theme_color: string;
  icons: PWAIcon[];
  orientation?: 'portrait' | 'landscape' | 'any';
}

export interface PWAIcon {
  src: string;
  sizes: string;
  type: string;
  purpose?: 'any' | 'maskable' | 'monochrome';
}

// ============================================================================
// Translation Types
// ============================================================================

export interface Translation {
  locale: string;
  key: string;
  value: string;
  updatedBy?: number;
  updatedAt: string;
}

export interface TranslationSet {
  locale: string;
  translations: Record<string, string>;
}

// ============================================================================
// Role & Permission Types (RBAC)
// ============================================================================

export interface Role {
  id: number;
  name: string;
  description?: string;
  permissions: string[];
  isSystem: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Permission {
  resource: string;
  action: 'create' | 'read' | 'update' | 'delete' | 'execute';
  scope?: 'own' | 'team' | 'all';
}

// ============================================================================
// Audit Log Types
// ============================================================================

export interface AuditLog {
  id: number;
  userId?: number;
  action: string;
  resourceType?: string;
  resourceId?: string;
  details?: Record<string, any>;
  ipAddress?: string;
  userAgent?: string;
  timestamp: string;
  status: 'success' | 'failure' | 'error';
}

// ============================================================================
// Utility Types
// ============================================================================

export type DateString = string; // ISO 8601 date string
export type UUID = string;

export interface ListOptions {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filters?: Record<string, any>;
}
