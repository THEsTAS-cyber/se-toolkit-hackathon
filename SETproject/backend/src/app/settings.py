"""Application settings using pydantic-settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application
    name: str = Field(default="App Service", alias="NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    address: str = Field(default="0.0.0.0", alias="ADDRESS")
    port: int = Field(default=8000, alias="PORT")
    reload: bool = Field(default=False, alias="RELOAD")
    cors_origins: list[str] = Field(default=[], alias="CORS_ORIGINS")

    # Database
    db_host: str = Field(default="postgres", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="db-app", alias="DB_NAME")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="postgres", alias="DB_PASSWORD")

    # PSPricing API
    pspricing_base_url: str = Field(
        default="https://psprices.com/api/b2b/demo/",
        alias="PSPRICING_BASE_URL",
    )
    pspricing_collection: str = Field(
        default="most-wanted-deals",
        alias="PSPRICING_COLLECTION",
    )
    pspricing_regions: list[str] = Field(
        default=[
            # === PSPricing B2B API — все 70 поддерживаемых регионов ===
            "ae", "ar", "at", "au", "be", "bg", "bh", "bo", "br", "ca",
            "ch", "cl", "cn", "cr", "cy", "cz", "de", "dk", "ec",
            "es", "fi", "fr", "gb", "gr", "gt", "hk", "hn", "hr", "hu",
            "id", "ie", "il", "in", "it", "jp", "kr", "kw", "lb",
            "lu", "mt", "mx", "my", "ni", "nl", "no", "nz", "om", "pa",
            "pe", "pl", "pt", "py", "qa", "ro", "ru", "sa", "se", "sg",
            "si", "sk", "sv", "th", "tr", "tw", "ua", "us", "uy", "za",
        ],
        alias="PSPRICING_REGIONS",
    )
    pspricing_sync_interval_hours: int = Field(
        default=12,
        alias="PSPRICING_SYNC_INTERVAL_HOURS",
    )

    # Auth
    jwt_secret: str = Field(default="change-me-in-production", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_hours: int = Field(default=720, alias="JWT_EXPIRE_HOURS")  # 30 days

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
