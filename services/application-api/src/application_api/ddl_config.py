"""Optional DDL resource limits, separate from required S1 diagnostics."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from application_api.config import ENV_FILE
from application_api.ddl_input import InputLimits


class DdlSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore", hide_input_in_errors=True)
    ddl_runtime_root: str | None = None
    ddl_max_files: int = Field(default=1024, ge=1)
    ddl_max_total_bytes: int = Field(default=64 * 1024 * 1024, ge=1)
    ddl_max_file_bytes: int = Field(default=64 * 1024 * 1024, ge=1)
    ddl_worker_timeout_seconds: int = Field(default=120, ge=1)

    def limits(self):
        return InputLimits(self.ddl_max_files, self.ddl_max_total_bytes, self.ddl_max_file_bytes)
