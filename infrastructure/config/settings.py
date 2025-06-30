from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from infrastructure.config.database import DatabaseSettings


class Settings(BaseSettings):
    """Основные настройки приложения."""

    # Настройки базы данных
    database: DatabaseSettings = DatabaseSettings()

    # Здесь могут быть другие настройки приложения
    # например, для API, кэширования, очередей и т.д.

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",  # Разрешаем дополнительные поля в конфигурации
    )


@lru_cache
def get_settings() -> Settings:
    """
    Получить настройки приложения.

    Функция кэширована с помощью @lru_cache, чтобы избежать
    повторного чтения файла конфигурации.
    """
    return Settings()
