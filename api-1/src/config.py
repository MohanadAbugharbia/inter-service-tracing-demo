from pydantic import (
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import (
    Literal,
    Self,
)
from .utils import singleton


@singleton
class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix = "api_",
    )

    application_name: str = "example-fastapi-1"

    environment: Literal["development", "testing", "staging", "production"] = "development"

    enable_fastapi_telemetry: bool = False
    enable_httpx_telemetry: bool = False

    enable_all_telemetry: bool = True

    tracing_batch_processor: bool = True

    api_2_base_url: str = "http://localhost:8001"


    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.enable_all_telemetry:
            self.enable_fastapi_telemetry = True
            self.enable_httpx_telemetry = True

        self.api_2_base_url = self._remove_trailing_slash(self.api_2_base_url)

        return self


    def _remove_trailing_slash(self, v: str) -> str:
        if v.endswith("/"):
            return v[:-1]
        return v


config = Config()
