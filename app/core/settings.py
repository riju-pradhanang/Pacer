from functools import lru_cache
from typing import Self

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEV_SECRET = 'dev-only-change-me'

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='PACER_', env_file='.env', extra='ignore')

    env: str = 'dev'
    database_url: str = 'postgresql+asyncpg://pacer:pacer@localhost:5432/pacer'
    redis_url: str = 'redis://localhost:6379/0'
    jwt_secret: SecretStr = SecretStr(_DEV_SECRET)
    access_token_ttl_s: int = 900
    refresh_token_ttl_s: int = 60 * 60 * 24 * 14
    log_level: str = 'INFO'

    @model_validator(mode='after')
    def _no_default_secret_in_prod(self) -> Self:
        if self.env == 'prod' and self.jwt_secret.get_secret_value() == _DEV_SECRET:
            raise ValueError('PACER_JWT_SECRET must be set when PACER_ENV=prod')
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()