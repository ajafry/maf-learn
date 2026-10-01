"""Configuration helpers for the workshop notebooks."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


class WorkshopConfigurationError(ValueError):
    """Raised when required workshop configuration is missing or still a placeholder."""


@dataclass(frozen=True)
class WorkshopSettings:
    """Environment-backed configuration shared by all lessons."""

    project_endpoint: str
    model: str
    agent_name: str | None = None
    agent_version: str | None = None

    @classmethod
    def from_env(
        cls,
        env_file: Path | str = DEFAULT_ENV_FILE,
        *,
        require_agent: bool = False,
    ) -> WorkshopSettings:
        """Load and validate workshop settings from a dotenv file."""
        load_dotenv(dotenv_path=env_file, override=False)

        project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "").strip()
        model = os.getenv("FOUNDRY_MODEL", "").strip()
        agent_name = os.getenv("FOUNDRY_AGENT_NAME", "").strip() or None
        agent_version = os.getenv("FOUNDRY_AGENT_VERSION", "").strip() or None

        missing = [
            name
            for name, value in (
                ("FOUNDRY_PROJECT_ENDPOINT", project_endpoint),
                ("FOUNDRY_MODEL", model),
            )
            if not value or _is_placeholder(value)
        ]
        if require_agent and (not agent_name or _is_placeholder(agent_name)):
            missing.append("FOUNDRY_AGENT_NAME")

        if missing:
            variables = ", ".join(missing)
            raise WorkshopConfigurationError(
                f"Set {variables} in {Path(env_file).name} before running this lesson. "
                "Start by copying values from your Microsoft Foundry project."
            )

        if not project_endpoint.startswith("https://"):
            raise WorkshopConfigurationError("FOUNDRY_PROJECT_ENDPOINT must be an HTTPS URL.")

        return cls(
            project_endpoint=project_endpoint.rstrip("/"),
            model=model,
            agent_name=agent_name,
            agent_version=agent_version,
        )

    def safe_summary(self) -> dict[str, str]:
        """Return non-secret configuration suitable for display in a notebook."""
        return {
            "project_endpoint": self.project_endpoint,
            "model": self.model,
            "agent_name": self.agent_name or "(not configured)",
            "agent_version": self.agent_version or "(latest / hosted agent)",
            "authentication": "DefaultAzureCredential (Microsoft Entra ID)",
        }


def create_credential() -> DefaultAzureCredential:
    """Create the credential chain used by the workshop.

    For the local workshop flow, run ``az login`` first. The same code can use a
    managed identity when moved to Azure without storing credentials in source.
    """
    return DefaultAzureCredential()


def create_chat_client(
    settings: WorkshopSettings,
    credential: DefaultAzureCredential | None = None,
) -> FoundryChatClient:
    """Create a Foundry model client from validated workshop settings."""
    return FoundryChatClient(
        project_endpoint=settings.project_endpoint,
        model=settings.model,
        credential=credential or create_credential(),
    )


def _is_placeholder(value: str) -> bool:
    upper_value = value.upper()
    return "YOUR-" in upper_value or "YOUR_" in upper_value or "<" in value or ">" in value
