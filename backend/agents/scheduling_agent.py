"""Scheduling Agent class with explicit model invocation."""
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
from typing import Any

from .framework import AcmeLoanAgentFramework
from .helpers import extract_reference_number
from .mcp_servers import call_mcp_server


class SchedulingAgent(AcmeLoanAgentFramework):
    AGENT_ID = "scheduling_agent"
    AGENT_NAME = "Scheduling Agent"
    VERSION = "1.0.0"
    MODEL_NAME = "amazon nova lite"
    BEDROCK_MODEL_ID = "amazon.nova-lite-v1:0"
    DESCRIPTION = "Schedules borrower, underwriting, and support meetings."
    MCP_SERVERS = ["Google Calendar", "Email", "Slack"]
    GUARDRAILS = {
        "mask_pii": None,
        "base64_prompt_detection": None,
        "credential_minimization": None,
        "inter_agent_authentication": None,
    }
    SYSTEM_PROMPT = "Coordinate calendar events and notify the relevant teams."

    async def call_agent_model(self, user_message: str, meeting_reference: str) -> str:
        _lineaje_messages = ([
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Meeting reference: {meeting_reference}\n"
                        f"Scheduling request: {user_message or 'Loan coordination meeting requested.'}\n\n"
                        "Draft a scheduling confirmation."
                    ),
                },
            ])
        # LINEAJE: enforce() `_lineaje_messages` at agent->llm pre_model — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:038a5b01f00a0088d87ea8ef93152cc9b2a36ea3d19877fadfdb5ac3796f2fac'
        _gr_client = _lineaje_load_gr_client()
        _lineaje_interaction_id = _gr_client.new_interaction_id()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:038a5b01f00a0088d87ea8ef93152cc9b2a36ea3d19877fadfdb5ac3796f2fac', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'file_path': 'backend/agents/scheduling_agent.py', 'line': 11, 'name': 'SchedulingAgent', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'destination': {'entity_type': 'llm', 'name': 'amazon nova lite', 'provider': '', 'version': ''}, 'identity': {'app': {'name': 'acme_loan_processor', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo', 'version': 'main'}, 'destination': {'entity_type': 'aimodel', 'name': 'Amazon Nova Lite', 'purl': 'pkg:aimodel/Amazon%20Nova%20Lite@v1:0', 'version': 'v1:0'}, 'source': {'entity_type': 'aiagent', 'name': 'SchedulingAgent', 'purl': 'pkg:aiagent/SchedulingAgent@1.0.0', 'version': '1.0.0'}}, 'invocation': {'file': 'backend/agents/scheduling_agent.py', 'function': 'SchedulingAgent.call_agent_model', 'line': 28}, 'file': 'backend/agents/scheduling_agent.py', 'line': 28, 'function': 'call_agent_model', 'agent_name': 'SchedulingAgent', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:e8923f047186c4c7'}, interaction_id=_lineaje_interaction_id)
        try:
            _lineaje_messages = _gr_client.enforce(_gr_site, _lineaje_messages, content_type='application/json', variable_name='_lineaje_messages', source_file=__file__, before_line=28)
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            raise
        return await self.call_bedrock_model(
            messages=_lineaje_messages,
            temperature=0.2,
            max_tokens=180,
        )

    async def handle(self, context: dict[str, Any]) -> dict[str, Any]:
        user_message = context.get("user_message", "")
        meeting_reference = extract_reference_number(user_message, prefix="MEET")
        # LINEAJE: enforce() `user_message` at agent->llm pre_model — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:ffe1354837ce0346bb61aa5011bbf7b31273aaf3703463eb21d4ffebb0fb0958'
        _lineaje_user_message_evidence = {'user_message': user_message, 'model': _lineaje_current_model(), 'project': 'tree'}
        _gr_client = _lineaje_load_gr_client()
        _lineaje_interaction_id = _gr_client.new_interaction_id()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:ffe1354837ce0346bb61aa5011bbf7b31273aaf3703463eb21d4ffebb0fb0958', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'file_path': 'backend/agents/scheduling_agent.py', 'line': 23, 'name': 'amazon.nova-lite-v1:0', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'destination': {'entity_type': 'llm', 'name': 'amazon nova lite', 'provider': '', 'version': ''}, 'identity': {'app': {'name': 'acme_loan_processor', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo', 'version': 'main'}, 'destination': {'entity_type': 'aimodel', 'name': 'Amazon Nova Lite', 'purl': 'pkg:aimodel/Amazon%20Nova%20Lite@v1:0', 'version': 'v1:0'}, 'source': {'entity_type': 'aiagent', 'name': 'amazon.nova-lite-v1:0', 'purl': 'pkg:aiagent/amazon.nova-lite-v1%3A0@1.0.0', 'version': '1.0.0'}}, 'invocation': {'file': 'backend/agents/scheduling_agent.py', 'function': 'SchedulingAgent.handle', 'line': 47}, 'file': 'backend/agents/scheduling_agent.py', 'line': 47, 'function': 'handle', 'agent_name': 'SchedulingAgent', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:610f7277c2499e58'}, interaction_id=_lineaje_interaction_id)
        try:
            _lineaje_user_message_evidence = await __import__('asyncio').to_thread(lambda: _gr_client.enforce(_gr_site, _lineaje_user_message_evidence, content_type='application/json'))
            user_message = _lineaje_user_message_evidence.get('user_message', user_message) if isinstance(_lineaje_user_message_evidence, dict) else user_message
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            raise
        model_output = await self.call_agent_model(user_message, meeting_reference)
        try:
            _lineaje_obs = _lineaje_load_gr_client()
            _lineaje_obs_site = _lineaje_obs.SiteDescriptor(site_id='site:sha256:840e435e7b66d9d9c29716ff9e66924e4802de22b192c510fe2ac99c53335b84', phase='', boundary={}, fail_mode='ALLOW', source_type='llm', destination_type='agent', project='tree', organization='', components={'file': 'backend/agents/scheduling_agent.py', 'line': 47, 'function': 'handle', 'agent_name': 'SchedulingAgent', 'agent_name_source': 'inferred_from_class', 'call_target': 'self.call_agent_model', 'source': {'entity_type': 'agent', 'file_path': 'backend/agents/scheduling_agent.py', 'line': 23, 'name': 'amazon.nova-lite-v1:0', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'destination': {'entity_type': 'llm', 'name': 'amazon nova lite', 'provider': '', 'version': ''}, 'identity': {'app': {'name': 'acme_loan_processor', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo', 'version': 'main'}, 'destination': {'entity_type': 'aimodel', 'name': 'Amazon Nova Lite', 'purl': 'pkg:aimodel/Amazon%20Nova%20Lite@v1:0', 'version': 'v1:0'}, 'source': {'entity_type': 'aiagent', 'name': 'amazon.nova-lite-v1:0', 'purl': 'pkg:aiagent/amazon.nova-lite-v1%3A0@1.0.0', 'version': '1.0.0'}}, 'invocation': {'file': 'backend/agents/scheduling_agent.py', 'function': 'SchedulingAgent.handle', 'line': 47}, 'boundary_id': 'bnd:610f7277c2499e58'}, observe_only=True, interaction_id=locals().get('_lineaje_interaction_id'))
            await __import__('asyncio').to_thread(lambda: _lineaje_obs.enforce(_lineaje_obs_site, {'activity': 'llm_to_agent'}, content_type='application/json'))
        except Exception:
            pass

        _lineaje_payload = (call_mcp_server(
                self.to_dict(),
                "Google Calendar",
                "create_event",
                {
                    "title": f"Borrower meeting {meeting_reference}",
                    "description": user_message or "Loan coordination meeting requested.",
                    "start": "2026-04-01T10:00:00-07:00",
                    "end": "2026-04-01T10:30:00-07:00",
                },
            ))
        # LINEAJE: enforce() `_lineaje_payload` at agent->tool pre_tool — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:9a071a3a21923977f3a2559eb4b5271d4fd0af6826eaf348f7fbc82baabe7285'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:9a071a3a21923977f3a2559eb4b5271d4fd0af6826eaf348f7fbc82baabe7285', phase='pre_tool', boundary={'source': 'agent_message', 'sink': 'tool_result'}, fail_mode='ALLOW_WITH_AUDIT', source_type='agent', destination_type='tool', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'file_path': 'backend/agents/scheduling_agent.py', 'line': 23, 'name': 'amazon.nova-lite-v1:0', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'identity': {'app': {'name': 'acme_loan_processor', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo', 'version': 'main'}, 'destination': {'entity_type': 'mcpserver', 'name': 'slack', 'purl': 'pkg:mcpserver/slack@post_message', 'version': 'post_message'}, 'source': {'entity_type': 'aiagent', 'name': 'amazon.nova-lite-v1:0', 'purl': 'pkg:aiagent/amazon.nova-lite-v1%3A0@1.0.0', 'version': '1.0.0'}}, 'invocation': {'file': 'backend/agents/scheduling_agent.py', 'function': 'SchedulingAgent.handle', 'line': 49}, 'destination': {'entity_type': 'mcp_server', 'file_path': 'backend/agents/scheduling_agent.py', 'line': 71, 'name': 'slack', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'file': 'backend/agents/scheduling_agent.py', 'line': 49, 'function': 'handle', 'agent_name': 'SchedulingAgent', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:17f72bb7dd352a82'})
        try:
            _lineaje_payload = _gr_client.enforce(_gr_site, _lineaje_payload, content_type='application/json', variable_name='_lineaje_payload', source_file=__file__, before_line=49)
        except _gr_client.GuardrailUnavailableError:
            pass
        mcp_activity = await asyncio.gather(
            _lineaje_payload,
            call_mcp_server(
                self.to_dict(),
                "Email",
                "send_email",
                {
                    "to": ["borrower@acme.example", "underwriting@acme.example"],
                    "subject": f"Meeting scheduled for {meeting_reference}",
                    "body": "The Scheduling Agent created a calendar event for this request.",
                },
            ),
            call_mcp_server(
                self.to_dict(),
                "Slack",
                "post_message",
                {
                    "channel": "#loan-ops",
                    "text": f"Scheduling Agent created meeting {meeting_reference}.",
                },
            ),
        )
        # LINEAJE: enforce() `mcp_activity` at tool->agent post_tool — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:f25d857d00787ae16e48643fa8427d88cd8eed7ead2ceb4f1898fe2508527568'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:f25d857d00787ae16e48643fa8427d88cd8eed7ead2ceb4f1898fe2508527568', phase='post_tool', boundary={'source': 'tool_result', 'sink': 'agent_message'}, fail_mode='ALLOW_WITH_AUDIT', source_type='tool', destination_type='agent', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'file_path': 'backend/agents/scheduling_agent.py', 'line': 23, 'name': 'amazon.nova-lite-v1:0', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'identity': {'app': {'name': 'acme_loan_processor', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo', 'version': 'main'}, 'destination': {'entity_type': 'mcpserver', 'name': 'slack', 'purl': 'pkg:mcpserver/slack@post_message', 'version': 'post_message'}, 'source': {'entity_type': 'aiagent', 'name': 'amazon.nova-lite-v1:0', 'purl': 'pkg:aiagent/amazon.nova-lite-v1%3A0@1.0.0', 'version': '1.0.0'}}, 'invocation': {'file': 'backend/agents/scheduling_agent.py', 'function': 'SchedulingAgent.handle', 'line': 49}, 'destination': {'entity_type': 'mcp_server', 'file_path': 'backend/agents/scheduling_agent.py', 'line': 71, 'name': 'slack', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'file': 'backend/agents/scheduling_agent.py', 'line': 49, 'function': 'handle', 'agent_name': 'SchedulingAgent', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:17f72bb7dd352a82'})
        try:
            mcp_activity = _gr_client.enforce(_gr_site, mcp_activity, content_type='application/json', variable_name='mcp_activity', source_file=__file__, before_line=49)
        except _gr_client.GuardrailUnavailableError:
            pass

        response = (
            f"Meeting reference: {meeting_reference}\n"
            f"Scheduling request: {user_message or 'No scheduling request provided.'}\n\n"
            f"Scheduling summary:\n{model_output}"
        )

        return {
            "response": response,
            "agent": self.AGENT_NAME,
            "model": self.MODEL_NAME,
            "framework": self.FRAMEWORK_NAME,
            "mcp_activity": mcp_activity,
        }


scheduling_agent = SchedulingAgent()
