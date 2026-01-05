"""Configuration management for PAskit application."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class AIProviderConfig(BaseModel):
    """Configuration for an AI provider."""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: Optional[str] = None
    enabled: bool = True


class RenderingConfig(BaseModel):
    """Rendering engine configuration."""
    target_fps: int = 60
    vsync: bool = True
    msaa_samples: int = 4
    background_color: list[float] = [0.1, 0.1, 0.15]


class WindowConfig(BaseModel):
    """Window configuration."""
    width: int = 1400
    height: int = 800
    chat_panel_width: int = 400
    maximized: bool = False


class Config(BaseModel):
    """Main application configuration."""

    # AI Providers
    openai: AIProviderConfig = Field(default_factory=AIProviderConfig)
    anthropic: AIProviderConfig = Field(default_factory=AIProviderConfig)
    ollama: AIProviderConfig = Field(default_factory=lambda: AIProviderConfig(
        base_url="http://localhost:11434"
    ))

    # Current provider selection
    current_provider: str = "openai"

    # Feature mode: student, competition, engineering
    feature_mode: str = "student"

    # Rendering
    rendering: RenderingConfig = Field(default_factory=RenderingConfig)

    # Window
    window: WindowConfig = Field(default_factory=WindowConfig)

    # Session
    auto_save_session: bool = True
    session_directory: str = "sessions"

    # Logging
    log_level: str = "INFO"
    log_to_file: bool = True

    @classmethod
    def get_config_path(cls) -> Path:
        """Get the configuration file path."""
        config_dir = Path.home() / ".paskit"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.yaml"

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file and environment."""
        # Load environment variables from .env file
        load_dotenv()

        config_path = cls.get_config_path()

        # Load from YAML if exists
        if config_path.exists():
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        # Override with environment variables
        env_overrides = cls._load_from_env()
        data = cls._merge_dicts(data, env_overrides)

        return cls(**data)

    @classmethod
    def _load_from_env(cls) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_config: Dict[str, Any] = {}

        # AI Provider API Keys
        if openai_key := os.getenv("OPENAI_API_KEY"):
            env_config.setdefault("openai", {})["api_key"] = openai_key

        if anthropic_key := os.getenv("ANTHROPIC_API_KEY"):
            env_config.setdefault("anthropic", {})["api_key"] = anthropic_key

        if ollama_url := os.getenv("OLLAMA_BASE_URL"):
            env_config.setdefault("ollama", {})["base_url"] = ollama_url

        # Current provider
        if provider := os.getenv("PASKIT_PROVIDER"):
            env_config["current_provider"] = provider

        # Log level
        if log_level := os.getenv("PASKIT_LOG_LEVEL"):
            env_config["log_level"] = log_level

        return env_config

    @staticmethod
    def _merge_dicts(base: Dict, override: Dict) -> Dict:
        """Recursively merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result

    def save(self) -> None:
        """Save configuration to file."""
        config_path = self.get_config_path()

        # Convert to dict and save
        data = self.model_dump(exclude_none=True)

        with open(config_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        provider_config = getattr(self, provider, None)
        if provider_config:
            return provider_config.api_key
        return None

    def set_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for a specific provider."""
        provider_config = getattr(self, provider, None)
        if provider_config:
            provider_config.api_key = api_key
            self.save()

    def get_base_url(self, provider: str) -> Optional[str]:
        """Get base URL for a specific provider."""
        provider_config = getattr(self, provider, None)
        if provider_config:
            return provider_config.base_url
        return None

    def set_base_url(self, provider: str, base_url: str) -> None:
        """Set base URL for a specific provider."""
        provider_config = getattr(self, provider, None)
        if provider_config:
            provider_config.base_url = base_url
            self.save()

    def set_provider_config(self, provider: str, api_key: str, base_url: Optional[str] = None, default_model: Optional[str] = None) -> None:
        """Set complete configuration for a provider."""
        provider_config = getattr(self, provider, None)
        if provider_config:
            provider_config.api_key = api_key
            if base_url is not None:
                provider_config.base_url = base_url
            if default_model is not None:
                provider_config.default_model = default_model
            self.save()

    def get_current_provider_config(self) -> Optional[AIProviderConfig]:
        """Get configuration for the currently selected provider."""
        return getattr(self, self.current_provider, None)
