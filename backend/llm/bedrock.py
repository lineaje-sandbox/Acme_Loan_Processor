"""
Amazon Bedrock LLM Client

Client for communicating with LLMs via Amazon Bedrock.

SECURITY NOTES (for Unifai demo):
- No input sanitization before sending to LLM
- No response validation
- AWS credential handling could be improved
- No rate limiting
"""
# Copyright (c) Lineaje, Inc. All rights reserved.
# Lineaje UnifAI guardrail  version=2.0.0-alpha
# Each enforce() call site below carries a SiteDescriptor with:
#   site_id            deterministic id for this exact call site (file +
#                      symbol + insertion point + pattern) — stable across
#                      re-scans, used to dedupe stub insertions and to look
#                      up this site's policy mapping at runtime.
#   The Guardrail resolves the policies a site checks at runtime.
def _lineaje_load_gr_client():
    """Lineaje-added: load gr_stub_client.py without a pip dependency (missing / broken: a pass-through client)."""
    import sys as _s, importlib.util as _ilu
    from pathlib import Path as _P
    n = "_lineaje_gr_stub_client"
    if n in _s.modules: return _s.modules[n]
    try:
        h = _P(__file__).resolve().parent
        _cand = next((d / "gr_stub_client.py" for d in [h, *h.parents][:8] if (d / "gr_stub_client.py").is_file()), h / "gr_stub_client.py")
        _spec = _ilu.spec_from_file_location(n, _cand)
        _s.modules[n] = _m = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_m); return _m
    except Exception:
        _s.modules.pop(n, None)
        return type('_lineaje_gr_unavailable', (), {'STUB_API': 999999, 'GuardrailUnavailableError': type('GuardrailUnavailableError', (PermissionError,), {}), 'SiteDescriptor': staticmethod(lambda *a, **k: None), 'new_interaction_id': staticmethod(lambda *a, **k: None), 'enforce': staticmethod(lambda _s, _p, *a, **k: _p), 'enforce_request': staticmethod(lambda _s, _p, *a, **k: _p), 'enforce_reply': staticmethod(lambda _s, _p, *a, **k: _p)})
def _lineaje_current_model():
    """Lineaje-added: reread the app's model setting for every request."""
    import os as _o
    from pathlib import Path as _P
    _keys = ("OPENROUTER_MODEL", "LLM_MODEL", "MODEL_NAME", "MODEL_ID", "OPENAI_MODEL", "ANTHROPIC_MODEL", "BEDROCK_MODEL_ID")
    _here = _P(__file__).resolve().parent
    for _path in (_here / ".env", *(_p / ".env" for _p in list(_here.parents)[:8])):
        if not _path.is_file(): continue
        try: _lines = _path.read_text(encoding="utf-8").splitlines()
        except OSError: continue
        _values = {}
        for _line in _lines:
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line: continue
            _key, _, _value = _line.partition("=")
            if _key.strip() in _keys: _values[_key.strip()] = _value.strip().strip(chr(34)).strip(chr(39))
        for _key in _keys:
            if _values.get(_key): return _values[_key]
    return next((_o.environ[_key].strip() for _key in _keys if _o.environ.get(_key, "").strip()), "")


import asyncio
import logging
import os
from typing import Any, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


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
            _lineaje_payload = ("Amazon Bedrock region not configured. "
                "Runtime LLM calls use OPENROUTER_API_KEY / OPENROUTER_MODEL.")
            # LINEAJE: enforce() `_lineaje_payload` at agent->log log_emit — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:b789cb324461f8c8c05fd970cb37c76fff0c9bcc5b1515135b3e61342c486927'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:b789cb324461f8c8c05fd970cb37c76fff0c9bcc5b1515135b3e61342c486927', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'identity': {'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}}, 'invocation': {'file': 'backend/llm/bedrock.py', 'line': 58, 'function': 'BedrockClient.__init__'}, 'file': 'backend/llm/bedrock.py', 'line': 58, 'function': '__init__', 'agent_name': 'BedrockClient', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json')
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            logger.debug(
                _lineaje_payload
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

        bedrock_messages, system_prompts = self._format_messages(messages)

        _lineaje_payload = "Sending request to Amazon Bedrock"
        # LINEAJE: enforce() `_lineaje_payload` at agent->log log_emit — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:d70f9b70d98a31611210c1895d1372cc6efa22d9dde78c6d8f8254d32e0744a8'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:d70f9b70d98a31611210c1895d1372cc6efa22d9dde78c6d8f8254d32e0744a8', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'identity': {'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}}, 'invocation': {'file': 'backend/llm/bedrock.py', 'line': 101, 'function': 'BedrockClient.chat'}, 'file': 'backend/llm/bedrock.py', 'line': 101, 'function': 'chat', 'agent_name': 'BedrockClient', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
        try:
            _lineaje_payload = await __import__('asyncio').to_thread(lambda: _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json'))
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        logger.info(
            _lineaje_payload,
            extra={
                "model": active_model,
                "region": active_region,
                "message_count": len(messages),
                "total_content_length": sum(
                    len(str(message.get("content", ""))) for message in messages
                ),
                # VULNERABILITY: Message content in logs
                "messages_preview": str(messages)[:200],
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

            _lineaje_payload = "Received response from Amazon Bedrock"
            # LINEAJE: enforce() `_lineaje_payload` at agent->log log_emit — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:43e225ac3346508e712e780a2bb0e8264d51c926772fdd2565befccc6952138b'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:43e225ac3346508e712e780a2bb0e8264d51c926772fdd2565befccc6952138b', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'identity': {'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}}, 'invocation': {'file': 'backend/llm/bedrock.py', 'line': 127, 'function': 'BedrockClient.chat'}, 'file': 'backend/llm/bedrock.py', 'line': 127, 'function': 'chat', 'agent_name': 'BedrockClient', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                _lineaje_payload = await __import__('asyncio').to_thread(lambda: _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json'))
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            logger.info(
                _lineaje_payload,
                extra={
                    "response_length": len(content),
                    # VULNERABILITY: Full response in logs
                    "response_preview": content[:200],
                },
            )

            # LINEAJE: enforce() `content` at agent->user_interface data_egress — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:f392b250728788b8ffc3037279c6c6bc1d8bec66609e94e41317f573cd756a15'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:f392b250728788b8ffc3037279c6c6bc1d8bec66609e94e41317f573cd756a15', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'identity': {'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}}, 'invocation': {'file': 'backend/llm/bedrock.py', 'line': 136, 'function': 'BedrockClient.chat'}, 'file': 'backend/llm/bedrock.py', 'line': 136, 'function': 'chat', 'agent_name': 'BedrockClient', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                content = _gr_client.enforce(_gr_site, content, content_type='text/plain')
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            return content

        except NoCredentialsError:
            _lineaje_payload = "Amazon Bedrock credentials not configured"
            # LINEAJE: enforce() `_lineaje_payload` at agent->log log_emit — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:ebda275c14f8ee88c0f2cfdda8d5a52a2f53ab8d3be166e4804e0464eb421014'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:ebda275c14f8ee88c0f2cfdda8d5a52a2f53ab8d3be166e4804e0464eb421014', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'identity': {'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}}, 'invocation': {'file': 'backend/llm/bedrock.py', 'line': 139, 'function': 'BedrockClient.chat'}, 'file': 'backend/llm/bedrock.py', 'line': 139, 'function': 'chat', 'agent_name': 'BedrockClient', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                _lineaje_payload = await __import__('asyncio').to_thread(lambda: _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json'))
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            logger.error(_lineaje_payload)
            return (
                "LLM service not configured. Please provide AWS credentials "
                "supported by boto3."
            )
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code", "Unknown")
            _lineaje_payload = f"Amazon Bedrock API error: {error_code}"
            # LINEAJE: enforce() `_lineaje_payload` at agent->log log_emit — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:8cde1a8d0d285a32dae5735e51d17994c4ba539700dca8f4f381e12d06bd4693'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:8cde1a8d0d285a32dae5735e51d17994c4ba539700dca8f4f381e12d06bd4693', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'identity': {'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}}, 'invocation': {'file': 'backend/llm/bedrock.py', 'line': 146, 'function': 'BedrockClient.chat'}, 'file': 'backend/llm/bedrock.py', 'line': 146, 'function': 'chat', 'agent_name': 'BedrockClient', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                _lineaje_payload = await __import__('asyncio').to_thread(lambda: _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json'))
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            logger.error(_lineaje_payload)
            return f"Error communicating with LLM: {error_code}"
        except (BotoCoreError, ValueError) as error:
            _lineaje_payload = f"Amazon Bedrock client error: {error}"
            # LINEAJE: enforce() `_lineaje_payload` at agent->log log_emit — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:37426a142855944df9754ce405cb36930f8dd3f4a19638675ee54fd5a0e4c51b'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:37426a142855944df9754ce405cb36930f8dd3f4a19638675ee54fd5a0e4c51b', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'identity': {'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}}, 'invocation': {'file': 'backend/llm/bedrock.py', 'line': 149, 'function': 'BedrockClient.chat'}, 'file': 'backend/llm/bedrock.py', 'line': 149, 'function': 'chat', 'agent_name': 'BedrockClient', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                _lineaje_payload = await __import__('asyncio').to_thread(lambda: _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json'))
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            logger.error(_lineaje_payload)
            return f"Error: {str(error)}"
        except Exception as error:
            _lineaje_payload = f"Amazon Bedrock unexpected error: {error}"
            # LINEAJE: enforce() `_lineaje_payload` at agent->log log_emit — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:a9982e7f1618bc84e61b2307d7b163adc9c25c05495e8e3e6fd3160069f0f941'
            _gr_client = _lineaje_load_gr_client()
            _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:a9982e7f1618bc84e61b2307d7b163adc9c25c05495e8e3e6fd3160069f0f941', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'identity': {'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}}, 'invocation': {'file': 'backend/llm/bedrock.py', 'line': 152, 'function': 'BedrockClient.chat'}, 'file': 'backend/llm/bedrock.py', 'line': 152, 'function': 'chat', 'agent_name': 'BedrockClient', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
            try:
                _lineaje_payload = await __import__('asyncio').to_thread(lambda: _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json'))
            except _gr_client.GuardrailUnavailableError:
                pass
            except PermissionError:
                pass
            logger.error(_lineaje_payload)
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

        # LINEAJE: enforce() `request` at agent->llm pre_model — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:2e764495ef89277f1b0d86a7eb51e1e2377b943d1701a35e36214d0be3f3620c'
        _gr_client = _lineaje_load_gr_client()
        _lineaje_interaction_id = _gr_client.new_interaction_id()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:2e764495ef89277f1b0d86a7eb51e1e2377b943d1701a35e36214d0be3f3620c', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'destination': {'entity_type': 'llm', 'name': 'amazon.nova-micro-v1:0', 'provider': 'amazon', 'version': ''}, 'identity': {'app': {'name': 'acme_loan_processor', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo', 'version': 'main'}, 'destination': {'entity_type': 'aimodel', 'name': 'amazon.nova-micro-v1:0', 'purl': 'pkg:aimodel/amazon.nova-micro-v1%3A0@v1:0', 'version': 'v1:0'}}, 'invocation': {'file': 'backend/llm/bedrock.py', 'function': 'BedrockClient._converse', 'line': 176}, 'file': 'backend/llm/bedrock.py', 'line': 176, 'function': '_converse', 'agent_name': 'BedrockClient', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:2686bdad07293029'}, interaction_id=_lineaje_interaction_id)
        try:
            if not hasattr(_gr_client, 'enforce_request'):
                __import__("logging").getLogger("lineaje.gr_client").error("gr_stub_client.py predates enforce_request (STUB_API 2): this site is NOT enforced; replace gr_stub_client.py with the current companion")
                raise _gr_client.GuardrailUnavailableError("stale gr_stub_client.py: no enforce_request")
            request = _gr_client.enforce_request(_gr_site, request, content_type='application/json')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            raise
        _lineaje_reply = client.converse(**request)
        # LINEAJE: enforce() `_lineaje_reply` at llm->agent post_model — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:76416cadb4662d94293cd56b4bf973532b261ee8f69d7d27cdc35befadae17eb'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:76416cadb4662d94293cd56b4bf973532b261ee8f69d7d27cdc35befadae17eb', phase='post_model', boundary={'source': 'model', 'sink': 'agent_message'}, fail_mode='BLOCK', source_type='llm', destination_type='agent', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'destination': {'entity_type': 'llm', 'name': 'amazon.nova-micro-v1:0', 'provider': 'amazon', 'version': ''}, 'identity': {'app': {'name': 'acme_loan_processor', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo', 'version': 'main'}, 'destination': {'entity_type': 'aimodel', 'name': 'amazon.nova-micro-v1:0', 'purl': 'pkg:aimodel/amazon.nova-micro-v1%3A0@v1:0', 'version': 'v1:0'}}, 'invocation': {'file': 'backend/llm/bedrock.py', 'function': 'BedrockClient._converse', 'line': 176}, 'file': 'backend/llm/bedrock.py', 'line': 176, 'function': '_converse', 'agent_name': 'BedrockClient', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:2686bdad07293029'}, interaction_id=locals().get('_lineaje_interaction_id'))
        try:
            if not hasattr(_gr_client, 'enforce_reply'):
                __import__("logging").getLogger("lineaje.gr_client").error("gr_stub_client.py predates enforce_reply (STUB_API 2): this site is NOT enforced; replace gr_stub_client.py with the current companion")
                raise _gr_client.GuardrailUnavailableError("stale gr_stub_client.py: no enforce_reply")
            _lineaje_reply = _gr_client.enforce_reply(_gr_site, _lineaje_reply, content_type='application/json')
        except _gr_client.GuardrailUnavailableError:
            pass
        return _lineaje_reply

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
            # VULNERABILITY: Context added without scanning
            messages.append(
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuery: {user_message}",
                }
            )
        else:
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
