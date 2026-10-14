"""
Amazon Bedrock LLM Client

Client for communicating with LLMs via Amazon Bedrock.

SECURITY NOTES (for Unifai demo):
- No input sanitization before sending to LLM
- No response validation
- AWS credential handling could be improved
- No rate limiting
"""

import asyncio
import logging
import os
from typing import Any, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from unifai_guard import sanitize_prompt, find_prompt_attacks, redact_pii, mask_pii, sanitize_messages, find_code_execution, remove_suspicious_content, remove_hidden_prompts, remove_encoded_prompts, remove_leetspeak_prompts, find_command_requests

logger = logging.getLogger(__name__)


def _sanitize_message_content_for_llm(content: Any) -> Any:
    if isinstance(content, str):
        content = redact_pii(content, categories=('ssn', 'year_of_birth', 'birthplace', 'phone', 'email', 'mothers_maiden_name', 'home_address', 'passport_number', 'drivers_license_number', 'taxpayer_id', 'credit_card', 'financial_account_number', 'fingerprints', 'retina_iris_scan', 'voice_signature', 'facial_image', 'medical_records', 'employee_id', 'school_id', 'vehicle_identification_number', 'ip_address', 'mac_address', 'fine_location', 'ethnicity', 'sexual_orientation', 'aws_access_key_id', 'aws_secret_access_key', 'gcp_service_account_key', 'azure_client_secret', 'private_key', 'password', 'api_key', 'oauth_token'))
        content = remove_hidden_prompts(content)
        content = remove_encoded_prompts(content)
        content = remove_leetspeak_prompts(content)
        content = sanitize_prompt(content)
        return content
    if isinstance(content, list):
        sanitized_content: list[Any] = []
        for item in content:
            if isinstance(item, dict):
                sanitized_item = dict(item)
                if isinstance(sanitized_item.get("text"), str):
                    text = sanitized_item["text"]
                    text = redact_pii(text, categories=('ssn', 'year_of_birth', 'birthplace', 'phone', 'email', 'mothers_maiden_name', 'home_address', 'passport_number', 'drivers_license_number', 'taxpayer_id', 'credit_card', 'financial_account_number', 'fingerprints', 'retina_iris_scan', 'voice_signature', 'facial_image', 'medical_records', 'employee_id', 'school_id', 'vehicle_identification_number', 'ip_address', 'mac_address', 'fine_location', 'ethnicity', 'sexual_orientation', 'aws_access_key_id', 'aws_secret_access_key', 'gcp_service_account_key', 'azure_client_secret', 'private_key', 'password', 'api_key', 'oauth_token'))
                    text = remove_hidden_prompts(text)
                    text = remove_encoded_prompts(text)
                    text = remove_leetspeak_prompts(text)
                    text = sanitize_prompt(text)
                    sanitized_item["text"] = text
                sanitized_content.append(sanitized_item)
            else:
                sanitized_content.append(item)
        return sanitized_content
    return content


def _sanitize_messages_for_llm(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sanitized = sanitize_messages(messages)
    sanitized_messages: list[dict[str, Any]] = []
    for message in sanitized:
        sanitized_message = dict(message)
        role = sanitized_message.get("role", "user")
        if role != "system":
            sanitized_message["content"] = _sanitize_message_content_for_llm(
                sanitized_message.get("content", "")
            )
        sanitized_messages.append(sanitized_message)
    return sanitized_messages


def _sanitize_context_for_llm(context: str) -> str:
    context = redact_pii(context, categories=('ssn', 'year_of_birth', 'birthplace', 'phone', 'email', 'mothers_maiden_name', 'home_address', 'passport_number', 'drivers_license_number', 'taxpayer_id', 'credit_card', 'financial_account_number', 'fingerprints', 'retina_iris_scan', 'voice_signature', 'facial_image', 'medical_records', 'employee_id', 'school_id', 'vehicle_identification_number', 'ip_address', 'mac_address', 'fine_location', 'ethnicity', 'sexual_orientation'))
    context = remove_suspicious_content(context)
    context = remove_hidden_prompts(context)
    context = remove_encoded_prompts(context)
    context = remove_leetspeak_prompts(context)
    context = sanitize_prompt(context)
    return context


def _sanitize_llm_output(content: str) -> str:
    if find_code_execution(content):
        return "Error: Unsafe LLM response blocked."
    return content


class BedrockClient:
    """
    Client for Amazon Bedrock Runtime.

    VULNERABILITY: Content sent to LLM without security checks.
    - No PII scanning before send
    - No prompt injection detection
    - No response validation
    """

    DEFAULT_MODEL = "amazon.nova-micro-v1:0"

    def __init__(
        self,
        model_id: Optional[str] = None,
        region: Optional[str] = None,
    ):
        """
        Initialize the Amazon Bedrock client.

        Args:
            model_id: Amazon Bedrock model ID (defaults to env var)
            region: AWS region for Bedrock Runtime (defaults to env vars)
        """
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID") or self.DEFAULT_MODEL
        self.region = region or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
        self.session = (
            boto3.session.Session(region_name=self.region)
            if self.region
            else boto3.session.Session()
        )

        if not (self.region or self.session.region_name):
            # Runtime LLM path uses OpenRouter; Bedrock is legacy/unused.
            logger.debug(
                "Amazon Bedrock region not configured. "
                "Runtime LLM calls use OPENROUTER_API_KEY / OPENROUTER_MODEL."
            )

    def _get_client(self):
        client_region = self.region or self.session.region_name
        if not client_region:
            raise ValueError("AWS region is required for Amazon Bedrock Runtime.")

        return self.session.client("bedrock-runtime", region_name=client_region)

    async def chat(
        self,
        messages: list[dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Send a conversation request to Amazon Bedrock.

        VULNERABILITY: Messages sent without security scanning.
        - User content not checked for PII
        - No prompt injection filtering
        - Response not validated

        Args:
            messages: List of message dicts with role and content
            model: Override model ID for this request
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            LLM response text
        """
        active_model = model or self.model_id
        active_region = self.region or self.session.region_name
        if not active_region:
            return "LLM service not configured. Please set AWS_REGION or AWS_DEFAULT_REGION."

        messages = _sanitize_messages_for_llm(messages)
        command_requests = find_command_requests(messages)
        if command_requests:
            return "Error: Command-execution requests are not allowed."
        prompt_attacks = find_prompt_attacks(messages)
        if prompt_attacks:
            return "Error: Prompt injection detected in request."
        bedrock_messages, system_prompts = self._format_messages(messages)

        logger.info(
            "Sending request to Amazon Bedrock",
            extra={
                "model": active_model,
                "region": active_region,
                "message_count": len(messages),
                "total_content_length": sum(
                    len(str(message.get("content", ""))) for message in messages
                ),
                # VULNERABILITY: Message content in logs
                "messages_preview": "<redacted>",
            },
        )

        try:
            response = await asyncio.to_thread(
                self._converse,
                active_model,
                bedrock_messages,
                system_prompts,
                temperature,
                max_tokens,
            )

            content = self._extract_text(response)
            content = _sanitize_llm_output(content)

            logger.info(
                "Received response from Amazon Bedrock",
                extra={
                    "response_length": len(content),
                    # VULNERABILITY: Full response in logs
                    "response_preview": "<redacted>",
                },
            )

            return content

        except NoCredentialsError:
            logger.error("Amazon Bedrock credentials not configured")
            return (
                "LLM service not configured. Please provide AWS credentials "
                "supported by boto3."
            )
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"Amazon Bedrock API error: {error_code}")
            return f"Error communicating with LLM: {error_code}"
        except (BotoCoreError, ValueError) as error:
            logger.error(f"Amazon Bedrock client error: {error}")
            return f"Error: {str(error)}"
        except Exception as error:
            logger.error(f"Amazon Bedrock unexpected error: {error}")
            return f"Error: {str(error)}"

    def _converse(
        self,
        model_id: str,
        messages: list[dict[str, Any]],
        system_prompts: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        client = self._get_client()

        request: dict[str, Any] = {
            "modelId": model_id,
            "messages": messages,
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
            },
        }
        if system_prompts:
            request["system"] = system_prompts

        return client.converse(**request)

    def _format_messages(
        self,
        messages: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        bedrock_messages: list[dict[str, Any]] = []
        system_prompts: list[dict[str, str]] = []

        for message in messages:
            role = message.get("role", "user")
            content = str(message.get("content", ""))

            if role == "system":
                system_prompts.append({"text": content})
                continue

            bedrock_role = "assistant" if role == "assistant" else "user"
            bedrock_messages.append(
                {
                    "role": bedrock_role,
                    "content": [{"text": content}],
                }
            )

        return bedrock_messages, system_prompts

    def _extract_text(self, response: dict[str, Any]) -> str:
        content_blocks = response.get("output", {}).get("message", {}).get("content", [])
        text_parts = [
            block["text"]
            for block in content_blocks
            if isinstance(block, dict) and block.get("text")
        ]
        return "\n".join(text_parts).strip()

    async def chat_with_context(
        self,
        user_message: str,
        system_prompt: str,
        context: Optional[str] = None,
    ) -> str:
        """
        Convenience method for chat with system prompt and optional context.

        VULNERABILITY: No content validation.
        """
        messages = [{"role": "system", "content": system_prompt}]

        if context:
            context = _sanitize_context_for_llm(context)
            user_message = _sanitize_message_content_for_llm(user_message)
            message_content = f"Context:\n{context}\n\nQuery: {user_message}"
            message_content = redact_pii(message_content, categories=('ssn', 'year_of_birth', 'birthplace', 'phone', 'email', 'mothers_maiden_name', 'home_address', 'passport_number', 'drivers_license_number', 'taxpayer_id', 'credit_card', 'financial_account_number', 'fingerprints', 'retina_iris_scan', 'voice_signature', 'facial_image', 'medical_records', 'employee_id', 'school_id', 'vehicle_identification_number', 'ip_address', 'mac_address', 'fine_location', 'ethnicity', 'sexual_orientation'))
            message_content = redact_pii(message_content, categories=('ssn', 'year_of_birth', 'birthplace', 'phone', 'email', 'mothers_maiden_name', 'home_address', 'passport_number', 'drivers_license_number', 'taxpayer_id', 'credit_card', 'financial_account_number', 'fingerprints', 'retina_iris_scan', 'voice_signature', 'facial_image', 'medical_records', 'employee_id', 'school_id', 'vehicle_identification_number', 'ip_address', 'mac_address', 'fine_location', 'ethnicity', 'sexual_orientation', 'aws_access_key_id', 'aws_secret_access_key', 'gcp_service_account_key', 'azure_client_secret', 'private_key', 'password', 'api_key', 'oauth_token'))
            message_content = remove_suspicious_content(message_content)
            messages.append(
                {
                    "role": "user",
                    "content": message_content,
                }
            )
        else:
            user_message = _sanitize_message_content_for_llm(user_message)
            user_message = redact_pii(user_message, categories=('ssn', 'year_of_birth', 'birthplace', 'phone', 'email', 'mothers_maiden_name', 'home_address', 'passport_number', 'drivers_license_number', 'taxpayer_id', 'credit_card', 'financial_account_number', 'fingerprints', 'retina_iris_scan', 'voice_signature', 'facial_image', 'medical_records', 'employee_id', 'school_id', 'vehicle_identification_number', 'ip_address', 'mac_address', 'fine_location', 'ethnicity', 'sexual_orientation', 'aws_access_key_id', 'aws_secret_access_key', 'gcp_service_account_key', 'azure_client_secret', 'private_key', 'password', 'api_key', 'oauth_token'))
            user_message = remove_suspicious_content(user_message)
            messages.append({"role": "user", "content": user_message})

        return await self.chat(messages)

    async def analyze_document(self, content: str) -> str:
        """
        Analyze document content using LLM.

        VULNERABILITY: Document content sent directly to LLM
        without PII scanning or threat detection.
        """
        # VULNERABILITY: No pre-LLM security checks
        return await self.chat_with_context(
            user_message="Please analyze this document and provide a summary.",
            system_prompt="You are a document analyst. Analyze the provided content and summarize key points.",
            context=content,
        )
