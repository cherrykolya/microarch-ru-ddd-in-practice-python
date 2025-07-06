from typing import Any, Dict

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


class DatabaseSettings(BaseSettings):
    """Настройки базы данных."""

    DRIVER: str = Field(default="postgresql+asyncpg")
    HOST: str = Field(default="localhost")
    PORT: int = Field(default=5432)
    USER: str = Field(default="username")
    PASSWORD: SecretStr = Field(default=SecretStr("secret"))
    DATABASE: str = Field(default="delivery")

    ECHO: bool = Field(default=False)
    POOL_SIZE: int = Field(default=50)

    @property
    def DSN(self) -> URL:
        """Получить DSN для подключения к базе данных."""
        return URL.create(
            drivername=self.DRIVER,
            username=self.USER,
            password=self.PASSWORD.get_secret_value(),
            host=self.HOST,
            port=self.PORT,
            database=self.DATABASE,
        )

    def get_sqlalchemy_config(self) -> Dict[str, Any]:
        """Получить конфигурацию для SQLAlchemy."""
        return {
            "echo": self.ECHO,
            "pool_size": self.POOL_SIZE,
            "future": True,
        }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DB_",  # Все переменные окружения должны начинаться с DB_
        case_sensitive=True,
        extra="allow",  # Разрешаем дополнительные поля в конфигурации
    )
