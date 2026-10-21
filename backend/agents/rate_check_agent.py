"""Rate Check Agent class with explicit OpenRouter + DeepSeek invocation."""
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


import logging
import os
import re
from typing import Any

from llm.openai_compatible import OpenAICompatibleClient

from .framework import AcmeLoanAgentFramework

logger = logging.getLogger(__name__)


class RateCheckAgent(AcmeLoanAgentFramework):
    AGENT_ID = "rate_check_agent"
    AGENT_NAME = "Rate_Check Agent"
    VERSION = "1.0.0"
    # Vulnerability: this agent runs on DeepSeek, which is NOT on the
    # organization's approved LLM list (AI_APP_SEC_006).
    OPENROUTER_MODEL = "deepseek/deepseek-r1"
    MODEL_NAME = "deepseek/deepseek-r1"
    BEDROCK_MODEL_ID = ""
    DESCRIPTION = "Checks lending-rate questions using DeepSeek through OpenRouter."
    MCP_SERVERS: list[str] = []
    GUARDRAILS = {
        "mask_pii": True,
        "base64_prompt_detection": True,
        "credential_minimization": True,
        "inter_agent_authentication": True,
    }
    SYSTEM_PROMPT = "Answer rate-check questions with short, practical lending-rate guidance."
    IS_ROUTABLE = True

    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self):
        super().__init__()
        self.openrouter_client = OpenAICompatibleClient(
            base_url=self.OPENROUTER_BASE_URL,
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

    def to_dict(self) -> dict[str, Any]:
        metadata = super().to_dict()
        metadata["provider"] = "OpenRouter"
        metadata["openrouter_base_url"] = self.OPENROUTER_BASE_URL
        metadata["openrouter_model"] = self.resolve_model()
        # LINEAJE: enforce() `metadata` at agent->user_interface data_egress — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:0df19c3582f994fd226b63d4b3c50449cc5e39c6b94467c9dc70cc89cfdf4dcd'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:0df19c3582f994fd226b63d4b3c50449cc5e39c6b94467c9dc70cc89cfdf4dcd', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'file_path': 'backend/agents/rate_check_agent.py', 'line': 15, 'name': 'RateCheckAgent'}, 'identity': {'source': {'entity_type': 'aiagent', 'name': 'RateCheckAgent', 'version': '1.0.0', 'purl': 'pkg:aiagent/RateCheckAgent@1.0.0'}, 'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}}, 'invocation': {'file': 'backend/agents/rate_check_agent.py', 'line': 49, 'function': 'RateCheckAgent.to_dict'}, 'file': 'backend/agents/rate_check_agent.py', 'line': 49, 'function': 'to_dict', 'agent_name': 'RateCheckAgent', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
        try:
            metadata = _gr_client.enforce(_gr_site, metadata, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return metadata

    def sanitize_user_message(self, user_message: str) -> tuple[str, bool]:
        sanitized = (user_message or "").strip() or "No rate request provided."
        suspicious_patterns = [
            re.compile(r"<!--.*?-->", re.DOTALL),
            re.compile(r"[A-Za-z0-9+/=]{24,}"),
            re.compile(r"\b(?:curl|wget|bash|sh|zsh|powershell|cmd\.exe|rm|chmod|python\s+-c|exec|eval|subprocess)\b", re.IGNORECASE),
            re.compile(r"\bc[\W_]*u[\W_]*r[\W_]*l\b", re.IGNORECASE),
            re.compile(r"\bc[4@]rl\b|\bw[6g]et\b|\br[mn]\b", re.IGNORECASE),
        ]

        blocked = False
        for pattern in suspicious_patterns:
            if pattern.search(sanitized):
                blocked = True
                sanitized = pattern.sub("<blocked_unsafe_content>", sanitized)

        return sanitized, blocked

    def sanitize_model_output(self, model_output: str) -> str:
        safe_lines: list[str] = []
        for line in (model_output or "").splitlines():
            if re.search(r"\b(?:eval|exec|subprocess|shell\s*=\s*True|os\.system)\b", line, re.IGNORECASE):
                continue
            safe_lines.append(line)
        return "\n".join(safe_lines).strip() or "Rate summary unavailable."

    async def call_agent_model(self, user_message: str) -> str:
        try:
            _lineaje_obs = _lineaje_load_gr_client()
            _lineaje_obs_site = _lineaje_obs.SiteDescriptor(site_id='site:sha256:8c146b9276a5fb202bdb07ccdd4c7c00ed27ac506b7e59d815f1a50fe7819af2', phase='', boundary={}, fail_mode='ALLOW', source_type='agent', destination_type='llm', project='tree', organization='', components={'file': 'backend/agents/rate_check_agent.py', 'line': 78, 'function': 'call_agent_model', 'agent_name': 'RateCheckAgent', 'agent_name_source': 'inferred_from_class', 'call_target': 'self.resolve_model', 'source': {'entity_type': 'agent', 'file_path': 'backend/agents/rate_check_agent.py', 'line': 15, 'name': 'RateCheckAgent', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'destination': {'entity_type': 'llm', 'name': 'deepseek-r1', 'provider': 'deepseek', 'version': ''}, 'identity': {'app': {'name': 'acme_loan_processor', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo', 'version': 'main'}, 'destination': {'entity_type': 'aimodel', 'name': 'DeepSeek', 'purl': 'pkg:aimodel/DeepSeek@r1', 'version': 'r1'}, 'source': {'entity_type': 'aiagent', 'name': 'RateCheckAgent', 'purl': 'pkg:aiagent/RateCheckAgent@1.0.0', 'version': '1.0.0'}}, 'invocation': {'file': 'backend/agents/rate_check_agent.py', 'function': 'RateCheckAgent.call_agent_model', 'line': 78}, 'boundary_id': 'bnd:3f225a4eb6ee72f3'}, observe_only=True)
            await __import__('asyncio').to_thread(lambda: _lineaje_obs.enforce(_lineaje_obs_site, {'activity': 'agent_to_llm'}, content_type='application/json'))
        except Exception:
            pass
        model = self.resolve_model()
        if not os.getenv("OPENROUTER_API_KEY"):
            return "LLM service not configured. Please set OPENROUTER_API_KEY."
        if not model:
            return "LLM service not configured. Please set OPENROUTER_MODEL."

        _lineaje_payload = "Rate check LLM request"
        # LINEAJE: enforce() `_lineaje_payload` at agent->log log_emit — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:1c5ab84b3fc1af40ad31a390eda6314849d3834d077e69f40bbf40f23c96917a'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:1c5ab84b3fc1af40ad31a390eda6314849d3834d077e69f40bbf40f23c96917a', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'file_path': 'backend/agents/rate_check_agent.py', 'line': 15, 'name': 'RateCheckAgent'}, 'identity': {'source': {'entity_type': 'aiagent', 'name': 'RateCheckAgent', 'version': '1.0.0', 'purl': 'pkg:aiagent/RateCheckAgent@1.0.0'}, 'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}}, 'invocation': {'file': 'backend/agents/rate_check_agent.py', 'line': 84, 'function': 'RateCheckAgent.call_agent_model'}, 'file': 'backend/agents/rate_check_agent.py', 'line': 84, 'function': 'call_agent_model', 'agent_name': 'RateCheckAgent', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
        try:
            _lineaje_payload = await __import__('asyncio').to_thread(lambda: _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json'))
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        logger.info(
            _lineaje_payload,
            extra={
                "agent": self.AGENT_ID,
                "model": model,
                "prompt_length": len(user_message or ""),
            },
        )
        model_output = await self.openrouter_client.chat(
            model=model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Rate check request:\n{user_message or 'No rate request provided.'}\n\n"
                        "Provide a concise rate check summary."
                    ),
                },
            ],
            temperature=0.2,
            # deepseek-r1 spends completion tokens on a hidden reasoning pass (still
            # counted even when excluded from the reply), so leave room for both.
            max_tokens=1500,
            # deepseek-r1 via Novita often returns the answer at the end of
            # `reasoning` with `content` empty; recover it from there.
            recover_answer_from_reasoning=True,
        )
        # LINEAJE: enforce() `model_output` at llm->agent post_model — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:316f6bb7fc1c34b0f8617fabf37103906353e32cc2baf1bbd3a50ed7cf430f01'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:316f6bb7fc1c34b0f8617fabf37103906353e32cc2baf1bbd3a50ed7cf430f01', phase='post_model', boundary={'source': 'model', 'sink': 'agent_message'}, fail_mode='BLOCK', source_type='llm', destination_type='agent', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'file_path': 'backend/agents/rate_check_agent.py', 'line': 15, 'name': 'RateCheckAgent', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'destination': {'entity_type': 'llm', 'name': 'deepseek-r1', 'provider': 'deepseek', 'version': ''}, 'identity': {'app': {'name': 'acme_loan_processor', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo', 'version': 'main'}, 'destination': {'entity_type': 'aimodel', 'name': 'DeepSeek', 'purl': 'pkg:aimodel/DeepSeek@r1', 'version': 'r1'}, 'source': {'entity_type': 'aiagent', 'name': 'RateCheckAgent', 'purl': 'pkg:aiagent/RateCheckAgent@1.0.0', 'version': '1.0.0'}}, 'invocation': {'file': 'backend/agents/rate_check_agent.py', 'function': 'RateCheckAgent.call_agent_model', 'line': 92}, 'file': 'backend/agents/rate_check_agent.py', 'line': 92, 'function': 'call_agent_model', 'agent_name': 'RateCheckAgent', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:3f225a4eb6ee72f3'}, interaction_id=locals().get('_lineaje_interaction_id'))
        try:
            model_output = _gr_client.enforce(_gr_site, model_output, content_type='application/json', variable_name='model_output', source_file=__file__, before_line=92)
        except _gr_client.GuardrailUnavailableError:
            pass
        _lineaje_payload = "Rate check LLM response"
        # LINEAJE: enforce() `_lineaje_payload` at agent->log log_emit — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:0cb9e2b33fbd67836f82b560578a5c2f4052b3d2c840e150c54d990051d41287'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:0cb9e2b33fbd67836f82b560578a5c2f4052b3d2c840e150c54d990051d41287', phase='log_emit', boundary={'source': 'log', 'sink': 'log'}, fail_mode='BLOCK', source_type='agent', destination_type='log', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'file_path': 'backend/agents/rate_check_agent.py', 'line': 15, 'name': 'RateCheckAgent'}, 'identity': {'source': {'entity_type': 'aiagent', 'name': 'RateCheckAgent', 'version': '1.0.0', 'purl': 'pkg:aiagent/RateCheckAgent@1.0.0'}, 'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}}, 'invocation': {'file': 'backend/agents/rate_check_agent.py', 'line': 112, 'function': 'RateCheckAgent.call_agent_model'}, 'file': 'backend/agents/rate_check_agent.py', 'line': 112, 'function': 'call_agent_model', 'agent_name': 'RateCheckAgent', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
        try:
            _lineaje_payload = await __import__('asyncio').to_thread(lambda: _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json'))
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        logger.info(
            _lineaje_payload,
            extra={
                "agent": self.AGENT_ID,
                "model": model,
                "response_length": len(model_output or ""),
            },
        )
        # LINEAJE: enforce() `model_output` at agent->user_interface data_egress — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:896092e51e52bd5287264ae5a196b0ac5a928f9aa60eb5890cbd5fb0b8f81ce0'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:896092e51e52bd5287264ae5a196b0ac5a928f9aa60eb5890cbd5fb0b8f81ce0', phase='data_egress', boundary={'source': 'agent_message', 'sink': 'user_interface'}, fail_mode='BLOCK', source_type='agent', destination_type='user_interface', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'file_path': 'backend/agents/rate_check_agent.py', 'line': 15, 'name': 'RateCheckAgent'}, 'identity': {'source': {'entity_type': 'aiagent', 'name': 'RateCheckAgent', 'version': '1.0.0', 'purl': 'pkg:aiagent/RateCheckAgent@1.0.0'}, 'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}}, 'invocation': {'file': 'backend/agents/rate_check_agent.py', 'line': 120, 'function': 'RateCheckAgent.call_agent_model'}, 'file': 'backend/agents/rate_check_agent.py', 'line': 120, 'function': 'call_agent_model', 'agent_name': 'RateCheckAgent', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True})
        try:
            model_output = _gr_client.enforce(_gr_site, model_output, content_type='text/plain')
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            pass
        return model_output

    async def handle(self, context: dict[str, Any]) -> dict[str, Any]:
        user_message = context.get("user_message", "")
        safe_user_message, blocked_unsafe_content = self.sanitize_user_message(user_message)
        prompt_message = safe_user_message
        if blocked_unsafe_content:
            prompt_message = (
                "A rate-check request contained blocked unsafe prompt content. "
                "Use only the remaining safe request details."
            )

        # LINEAJE: enforce() `prompt_message` at agent->llm pre_model — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:30aaea03eb1d3a35bc49aaf6d4a5ef84377dbc654bf1cc6c96b229b82c46d071'
        _lineaje_prompt_message_evidence = {'prompt_message': prompt_message, 'model': _lineaje_current_model(), 'project': 'tree'}
        _gr_client = _lineaje_load_gr_client()
        _lineaje_interaction_id = _gr_client.new_interaction_id()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:30aaea03eb1d3a35bc49aaf6d4a5ef84377dbc654bf1cc6c96b229b82c46d071', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'file_path': 'backend/agents/rate_check_agent.py', 'line': 15, 'name': 'RateCheckAgent'}, 'destination': {'entity_type': 'llm', 'name': 'deepseek-r1', 'version': '', 'provider': 'deepseek'}, 'identity': {'source': {'entity_type': 'aiagent', 'name': 'RateCheckAgent', 'version': '1.0.0', 'purl': 'pkg:aiagent/RateCheckAgent@1.0.0'}, 'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}, 'destination': {'entity_type': 'aimodel', 'name': 'DeepSeek', 'version': 'r1', 'purl': 'pkg:aimodel/DeepSeek@r1'}}, 'invocation': {'file': 'backend/agents/rate_check_agent.py', 'line': 132, 'function': 'RateCheckAgent.handle'}, 'file': 'backend/agents/rate_check_agent.py', 'line': 132, 'function': 'handle', 'agent_name': 'RateCheckAgent', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True}, interaction_id=_lineaje_interaction_id)
        try:
            _lineaje_prompt_message_evidence = await __import__('asyncio').to_thread(lambda: _gr_client.enforce(_gr_site, _lineaje_prompt_message_evidence, content_type='application/json'))
            prompt_message = _lineaje_prompt_message_evidence.get('prompt_message', prompt_message) if isinstance(_lineaje_prompt_message_evidence, dict) else prompt_message
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            raise
        model_output = self.sanitize_model_output(await self.call_agent_model(prompt_message))
        try:
            _lineaje_obs = _lineaje_load_gr_client()
            _lineaje_obs_site = _lineaje_obs.SiteDescriptor(site_id='site:sha256:edfb9365daf1039787bedb07cdbf6a24ab3ee7dbf14348f4a6af479a42babece', phase='', boundary={}, fail_mode='ALLOW', source_type='llm', destination_type='agent', project='tree', organization='', components={'file': 'backend/agents/rate_check_agent.py', 'line': 132, 'function': 'handle', 'agent_name': 'RateCheckAgent', 'agent_name_source': 'inferred_from_class', 'call_target': 'self.sanitize_model_output', 'not_on_graph': True}, observe_only=True, interaction_id=locals().get('_lineaje_interaction_id'))
            await __import__('asyncio').to_thread(lambda: _lineaje_obs.enforce(_lineaje_obs_site, {'activity': 'llm_to_agent'}, content_type='application/json'))
        except Exception:
            pass

        response = (
            f"Using model: {self.resolve_model()}\n\n"
            f"Rate check request: {safe_user_message}\n\n"
            f"Rate summary:\n{model_output}"
        )

        return {
            "response": response,
            "agent": self.AGENT_NAME,
            "model": self.resolve_model(),
            "framework": self.FRAMEWORK_NAME,
            "provider": "OpenRouter",
        }


rate_check_agent = RateCheckAgent()
