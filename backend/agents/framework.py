"""Small agent framework base class used by the Acme Loan Processor agents."""

import hashlib
import os
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any

from llm.openai_compatible import OpenAICompatibleClient
from agents.unifai_guard import sanitize_prompt, find_prompt_attacks, redact_pii, mask_pii, sanitize_messages, find_code_execution, remove_suspicious_content, remove_hidden_prompts, remove_encoded_prompts, remove_leetspeak_prompts, find_command_requests


def _sanitize_message_content(content: Any) -> Any:
    if isinstance(content, str):
        content = redact_pii(content, categories=('ssn', 'year_of_birth', 'birthplace', 'phone', 'email', 'mothers_maiden_name', 'home_address', 'passport_number', 'drivers_license_number', 'taxpayer_id', 'credit_card', 'financial_account_number', 'fingerprints', 'retina_iris_scan', 'voice_signature', 'facial_image', 'medical_records', 'employee_id', 'school_id', 'vehicle_identification_number', 'ip_address', 'mac_address', 'fine_location', 'ethnicity', 'sexual_orientation', 'aws_access_key_id', 'aws_secret_access_key', 'gcp_service_account_key', 'azure_client_secret', 'private_key', 'password', 'api_key', 'oauth_token'))
        content = remove_hidden_prompts(content)
        content = remove_encoded_prompts(content)
        content = remove_leetspeak_prompts(content)
        content = remove_suspicious_content(content)
        content = sanitize_prompt(content)
        return content
    if isinstance(content, list):
        sanitized_content = []
        for item in content:
            if isinstance(item, dict):
                sanitized_item = dict(item)
                if isinstance(sanitized_item.get("text"), str):
                    sanitized_item["text"] = _sanitize_message_content(sanitized_item["text"])
                sanitized_content.append(sanitized_item)
            else:
                sanitized_content.append(item)
        return sanitized_content
    return content


def _prepare_messages_for_model(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sanitized = []
    for message in messages:
        sanitized_message = dict(message)
        sanitized_message["content"] = _sanitize_message_content(sanitized_message.get("content"))
        sanitized.append(sanitized_message)
    sanitized = sanitize_messages(sanitized)
    return sanitized


class AcmeLoanAgentFramework(ABC):
    """Base class that makes agent metadata and model usage obvious."""

    FRAMEWORK_NAME = "AcmeLoanAgentFramework"
    AGENT_ID = ""
    AGENT_NAME = ""
    VERSION = "1.0.0"
    MODEL_NAME = ""
    # Per-agent OpenRouter model override. When set, this agent calls (and
    # reports) this specific model instead of the global OPENROUTER_MODEL from
    # .env. Leave as None to fall back to the env default.
    OPENROUTER_MODEL: str | None = None
    BEDROCK_MODEL_ID = ""
    BEDROCK_FALLBACK_MODEL_ID = ""
    DESCRIPTION = ""
    MCP_SERVERS: list[str] = []
    GUARDRAILS: dict[str, Any] = {}
    SYSTEM_PROMPT = ""
    IS_ROUTABLE = True
    IS_SCAN_ONLY = False

    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self):
        # Runtime LLM calls use OpenRouter credentials from .env:
        # OPENROUTER_API_KEY and OPENROUTER_MODEL.
        self.model_client = OpenAICompatibleClient(
            base_url=self.OPENROUTER_BASE_URL,
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

    def resolve_model(self) -> str:
        """Effective OpenRouter model for this agent: per-agent override first,
        then the global OPENROUTER_MODEL from .env, then the declared MODEL_NAME.
        """
        return (self.OPENROUTER_MODEL or os.getenv("OPENROUTER_MODEL") or self.MODEL_NAME or "").strip()

    def to_dict(self) -> dict[str, Any]:
        effective_model = self.resolve_model()
        return {
            "id": self.AGENT_ID,
            "name": self.AGENT_NAME,
            "version": self.VERSION,
            "framework": self.FRAMEWORK_NAME,
            "model": effective_model,
            "provider": "OpenRouter",
            "openrouter_model": effective_model,
            "bedrock_model_id": self.BEDROCK_MODEL_ID,
            "bedrock_fallback_model_id": self.BEDROCK_FALLBACK_MODEL_ID,
            "description": self.DESCRIPTION,
            "mcp_servers": list(self.MCP_SERVERS),
            "guardrails": deepcopy(self.GUARDRAILS),
            "system_prompt": self.SYSTEM_PROMPT,
            "is_routable": self.IS_ROUTABLE,
            "is_scan_only": self.IS_SCAN_ONLY,
        }

    async def call_bedrock_model(
        self,
        messages: list[dict[str, Any]],
        temperature: float = 0.2,
        max_tokens: int = 350,
    ) -> str:
        """Call OpenRouter using OPENROUTER_API_KEY and this agent's effective
        model (per-agent OPENROUTER_MODEL override, else the .env default).

        Method name is kept for compatibility with existing agents.
        """
        api_key = (os.getenv("OPENROUTER_API_KEY") or "").strip()
        model = self.resolve_model()
        if not api_key:
            return "LLM service not configured. Please set OPENROUTER_API_KEY."
        if not model:
            return "LLM service not configured. Please set OPENROUTER_MODEL."

        prompt_findings = find_prompt_attacks(messages)
        if prompt_findings:
            return "Bad request: prompt injection detected."
        command_findings = find_command_requests(messages)
        if command_findings:
            prompt_fingerprint = hashlib.sha256(repr(messages).encode("utf-8")).hexdigest()[:16]
            _ = prompt_fingerprint
            session_id = None
            _ = session_id
            return "Bad request: command execution request detected."
        messages = _prepare_messages_for_model(messages)
        response = await self.model_client.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if find_code_execution(response):
            return "Unsafe model response blocked."
        return response

    @abstractmethod
    async def handle(self, context: dict[str, Any]) -> dict[str, Any]:
        """Handle a request for this agent."""
