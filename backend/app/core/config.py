"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""
from typing import List, Literal
from pydantic import Field, field_validator, PostgresDsn, MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="Application", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: Literal["development", "staging", "production"] = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    reload: bool = Field(default=False, alias="RELOAD")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        alias="CORS_ORIGINS"
    )

    # Frontend URL for OAuth redirects
    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")

    # Security
    secret_key: str = Field(..., alias="SECRET_KEY")
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    password_reset_token_expire_minutes: int = Field(default=30, alias="PASSWORD_RESET_TOKEN_EXPIRE_MINUTES")
    max_login_attempts: int = Field(default=5, alias="MAX_LOGIN_ATTEMPTS")
    account_lockout_duration: int = Field(default=30, alias="ACCOUNT_LOCKOUT_DURATION")  # in minutes

    # Database Configuration
    db_type: Literal["postgresql", "sqlserver"] = Field(default="postgresql", alias="DB_TYPE")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="postgres", alias="DB_PASSWORD")
    db_name: str = Field(default="appdb", alias="DB_NAME")
    db_echo: bool = Field(default=False, alias="DB_ECHO")
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")

    # SQL Server specific
    mssql_driver: str = Field(default="ODBC Driver 18 for SQL Server", alias="MSSQL_DRIVER")
    mssql_trust_certificate: bool = Field(default=True, alias="MSSQL_TRUST_CERTIFICATE")

    # MongoDB
    mongo_uri: str = Field(default="mongodb://localhost:27017", alias="MONGO_URI")
    mongo_db_name: str = Field(default="appdb", alias="MONGO_DB_NAME")
    mongo_min_pool_size: int = Field(default=10, alias="MONGO_MIN_POOL_SIZE")
    mongo_max_pool_size: int = Field(default=100, alias="MONGO_MAX_POOL_SIZE")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_session_db: int = Field(default=1, alias="REDIS_SESSION_DB")
    redis_cache_db: int = Field(default=2, alias="REDIS_CACHE_DB")
    redis_max_connections: int = Field(default=50, alias="REDIS_MAX_CONNECTIONS")

    # Authentication
    use_firebase: bool = Field(default=False, alias="USE_FIREBASE")
    enable_social_auth: bool = Field(default=True, alias="ENABLE_SOCIAL_AUTH")
    enable_mfa: bool = Field(default=True, alias="ENABLE_MFA")

    # Firebase
    firebase_project_id: str = Field(default="", alias="FIREBASE_PROJECT_ID")
    firebase_credentials_path: str = Field(default="", alias="FIREBASE_CREDENTIALS_PATH")

    # OAuth Providers
    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(default="", alias="GOOGLE_REDIRECT_URI")

    microsoft_client_id: str = Field(default="", alias="MICROSOFT_CLIENT_ID")
    microsoft_client_secret: str = Field(default="", alias="MICROSOFT_CLIENT_SECRET")
    microsoft_redirect_uri: str = Field(default="", alias="MICROSOFT_REDIRECT_URI")
    microsoft_tenant: str = Field(default="common", alias="MICROSOFT_TENANT")

    facebook_app_id: str = Field(default="", alias="FACEBOOK_APP_ID")
    facebook_app_secret: str = Field(default="", alias="FACEBOOK_APP_SECRET")
    facebook_redirect_uri: str = Field(default="", alias="FACEBOOK_REDIRECT_URI")

    apple_client_id: str = Field(default="", alias="APPLE_CLIENT_ID")  # Service ID
    apple_team_id: str = Field(default="", alias="APPLE_TEAM_ID")
    apple_key_id: str = Field(default="", alias="APPLE_KEY_ID")
    apple_private_key: str = Field(default="", alias="APPLE_PRIVATE_KEY")  # Content of .p8 file
    apple_redirect_uri: str = Field(default="", alias="APPLE_REDIRECT_URI")

    # MFA Providers
    twilio_account_sid: str = Field(default="", alias="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(default="", alias="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str = Field(default="", alias="TWILIO_PHONE_NUMBER")
    twilio_verify_service_sid: str = Field(default="", alias="TWILIO_VERIFY_SERVICE_SID")

    # Duo Auth API (for push authentication)
    duo_auth_ikey: str = Field(default="", alias="DUO_AUTH_IKEY")
    duo_auth_skey: str = Field(default="", alias="DUO_AUTH_SKEY")
    duo_auth_host: str = Field(default="", alias="DUO_AUTH_HOST")

    # Duo Admin API (for user management)
    duo_admin_ikey: str = Field(default="", alias="DUO_ADMIN_IKEY")
    duo_admin_skey: str = Field(default="", alias="DUO_ADMIN_SKEY")
    duo_admin_host: str = Field(default="", alias="DUO_ADMIN_HOST")

    # SendGrid Configuration (for Email OTP)
    sendgrid_api_key: str = Field(default="", alias="SENDGRID_API_KEY")
    sendgrid_from_email: str = Field(default="noreply@yourdomain.com", alias="SENDGRID_FROM_EMAIL")
    sendgrid_from_name: str = Field(default="Application", alias="SENDGRID_FROM_NAME")

    # Email Configuration
    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="noreply@yourdomain.com", alias="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="Application", alias="SMTP_FROM_NAME")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")

    # reCAPTCHA
    recaptcha_enabled: bool = Field(default=True, alias="RECAPTCHA_ENABLED")
    recaptcha_site_key_v3: str = Field(default="", alias="RECAPTCHA_SITE_KEY_V3")
    recaptcha_secret_key_v3: str = Field(default="", alias="RECAPTCHA_SECRET_KEY_V3")
    recaptcha_site_key_v2: str = Field(default="", alias="RECAPTCHA_SITE_KEY_V2")
    recaptcha_secret_key_v2: str = Field(default="", alias="RECAPTCHA_SECRET_KEY_V2")
    recaptcha_v3_threshold: float = Field(default=0.5, alias="RECAPTCHA_V3_THRESHOLD")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_login_attempts: int = Field(default=5, alias="RATE_LIMIT_LOGIN_ATTEMPTS")
    rate_limit_login_window_minutes: int = Field(default=15, alias="RATE_LIMIT_LOGIN_WINDOW_MINUTES")
    rate_limit_mfa_attempts: int = Field(default=3, alias="RATE_LIMIT_MFA_ATTEMPTS")
    rate_limit_mfa_window_minutes: int = Field(default=5, alias="RATE_LIMIT_MFA_WINDOW_MINUTES")
    rate_limit_api_requests: int = Field(default=100, alias="RATE_LIMIT_API_REQUESTS")
    rate_limit_api_window_minutes: int = Field(default=1, alias="RATE_LIMIT_API_WINDOW_MINUTES")

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO", alias="LOG_LEVEL")
    log_format: Literal["json", "text"] = Field(default="json", alias="LOG_FORMAT")
    log_file_enabled: bool = Field(default=True, alias="LOG_FILE_ENABLED")
    log_file_path: str = Field(default="logs/app.log", alias="LOG_FILE_PATH")
    log_file_max_bytes: int = Field(default=10485760, alias="LOG_FILE_MAX_BYTES")
    log_file_backup_count: int = Field(default=5, alias="LOG_FILE_BACKUP_COUNT")

    # Monitoring
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, alias="METRICS_PORT")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def database_url(self) -> str:
        """Generate database URL based on DB type."""
        if self.db_type == "postgresql":
            return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        elif self.db_type == "sqlserver":
            driver = self.mssql_driver.replace(" ", "+")
            trust_cert = "yes" if self.mssql_trust_certificate else "no"
            return (
                f"mssql+aioodbc://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
                f"?driver={driver}&TrustServerCertificate={trust_cert}"
            )
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"


# Global settings instance
settings = Settings()
