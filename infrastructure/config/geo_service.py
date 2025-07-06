from pydantic_settings import BaseSettings, SettingsConfigDict


class GeoServiceSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5004

    model_config = SettingsConfigDict(env_file=".env", env_prefix="GEO_SERVICE", extra="allow")
