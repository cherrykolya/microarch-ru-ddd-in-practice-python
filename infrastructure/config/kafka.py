from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    BROKERS: str = ""
    SECURITY_PROTOCOL: str = ""
    SASL_MECHANISM: str = "PLAIN"
    SASL_PLAIN_USERNAME: str = ""
    SASL_PLAIN_PASSWORD: str = ""

    BASKET_CONFIRMED_TOPIC: str = "basket.confirmed"
    BASKET_CONFIRMED_GROUP_ID: str = "basket-confirmed-group"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="kafka_", extra="allow")
