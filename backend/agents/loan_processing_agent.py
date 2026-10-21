"""Loan Processing Agent class with explicit model invocation."""
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
from .helpers import build_file_summary, extract_reference_number
from .mcp_servers import call_mcp_server


class LoanProcessingAgent(AcmeLoanAgentFramework):
    AGENT_ID = "loan_processing_agent"
    AGENT_NAME = "Loan Processing Agent"
    VERSION = "1.0.0"
    MODEL_NAME = "gpt-4o mini"
    BEDROCK_MODEL_ID = ""
    DESCRIPTION = "Handles loan application intake, borrower updates, and loan package generation."
    MCP_SERVERS = ["Docx", "Excel", "Email"]
    GUARDRAILS = {
        "mask_pii": None,
        "base64_prompt_detection": None,
        "credential_minimization": None,
        "inter_agent_authentication": None,
    }
    SYSTEM_PROMPT = "Process loan requests, summarize borrower context, and prepare follow-up actions."
    IS_ROUTABLE = False
    IS_SCAN_ONLY = True

    async def call_agent_model(self, user_message: str, file_summary: str) -> str:
        _lineaje_messages = ([
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Loan request:\n{user_message or 'No user message provided.'}\n\n"
                        f"File summary:\n{file_summary}\n\n"
                        "Draft a concise loan processing next-step summary."
                    ),
                },
            ])
        # LINEAJE: enforce() `_lineaje_messages` at agent->llm pre_model — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:8f56aae4478c8cd3d5ba51648a300f1757dad3064b26a4b9198c80b161a99e07'
        _lineaje__lineaje_messages_evidence = {'_lineaje_messages': _lineaje_messages, 'model': self.MODEL_NAME, 'project': 'tree'}
        _gr_client = _lineaje_load_gr_client()
        _lineaje_interaction_id = _gr_client.new_interaction_id()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:8f56aae4478c8cd3d5ba51648a300f1757dad3064b26a4b9198c80b161a99e07', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'file_path': 'backend/agents/loan_processing_agent.py', 'line': 11, 'name': 'LoanProcessingAgent', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'destination': {'entity_type': 'llm', 'name': 'gpt-4o mini', 'provider': 'openai', 'version': ''}, 'identity': {'app': {'name': 'acme_loan_processor', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo', 'version': 'main'}, 'destination': {'entity_type': 'aimodel', 'name': 'GPT', 'purl': 'pkg:aimodel/GPT@4o mini', 'version': '4o mini'}, 'source': {'entity_type': 'aiagent', 'name': 'LoanProcessingAgent', 'purl': 'pkg:aiagent/LoanProcessingAgent@1.0.0', 'version': '1.0.0'}}, 'invocation': {'file': 'backend/agents/loan_processing_agent.py', 'function': 'LoanProcessingAgent.call_agent_model', 'line': 30}, 'file': 'backend/agents/loan_processing_agent.py', 'line': 30, 'function': 'call_agent_model', 'agent_name': 'LoanProcessingAgent', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:ab03f691f7c8a024'}, interaction_id=_lineaje_interaction_id)
        try:
            _lineaje__lineaje_messages_evidence = await __import__('asyncio').to_thread(lambda: _gr_client.enforce(_gr_site, _lineaje__lineaje_messages_evidence, content_type='application/json'))
            _lineaje_messages = _lineaje__lineaje_messages_evidence.get('_lineaje_messages', _lineaje_messages) if isinstance(_lineaje__lineaje_messages_evidence, dict) else _lineaje_messages
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            raise
        return await self.model_client.chat(
            model=self.MODEL_NAME,
            messages=_lineaje_messages,
            temperature=0.2,
            max_tokens=250,
        )

    async def handle(self, context: dict[str, Any]) -> dict[str, Any]:
        user_message = context.get("user_message", "")
        file_summary = build_file_summary(context.get("file_contents", []))
        loan_number = extract_reference_number(user_message, prefix="LOAN")
        # LINEAJE: enforce() `user_message` at agent->llm pre_model — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:9a9ccef0ab9d02e67bc618e1d8b5c69e7027d86e8438dc2c7db423a766187a31'
        _lineaje_user_message_evidence = {'user_message': user_message, 'model': _lineaje_current_model(), 'project': 'tree'}
        _gr_client = _lineaje_load_gr_client()
        _lineaje_interaction_id = _gr_client.new_interaction_id()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:9a9ccef0ab9d02e67bc618e1d8b5c69e7027d86e8438dc2c7db423a766187a31', phase='pre_model', boundary={'source': 'agent_message', 'sink': 'model'}, fail_mode='BLOCK', source_type='agent', destination_type='llm', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'file_path': 'backend/agents/loan_processing_agent.py', 'line': 11, 'name': 'LoanProcessingAgent'}, 'destination': {'entity_type': 'llm', 'name': 'gpt-4o mini', 'version': '', 'provider': 'openai'}, 'identity': {'source': {'entity_type': 'aiagent', 'name': 'LoanProcessingAgent', 'version': '1.0.0', 'purl': 'pkg:aiagent/LoanProcessingAgent@1.0.0'}, 'app': {'name': 'acme_loan_processor', 'version': 'main', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo'}, 'destination': {'entity_type': 'aimodel', 'name': 'GPT', 'version': '4o mini', 'purl': 'pkg:aimodel/GPT@4o mini'}}, 'invocation': {'file': 'backend/agents/loan_processing_agent.py', 'line': 51, 'function': 'LoanProcessingAgent.handle'}, 'file': 'backend/agents/loan_processing_agent.py', 'line': 51, 'function': 'handle', 'agent_name': 'LoanProcessingAgent', 'agent_name_source': 'inferred_from_class', 'not_on_graph': True}, interaction_id=_lineaje_interaction_id)
        try:
            _lineaje_user_message_evidence = await __import__('asyncio').to_thread(lambda: _gr_client.enforce(_gr_site, _lineaje_user_message_evidence, content_type='application/json'))
            user_message = _lineaje_user_message_evidence.get('user_message', user_message) if isinstance(_lineaje_user_message_evidence, dict) else user_message
        except _gr_client.GuardrailUnavailableError:
            pass
        except PermissionError:
            raise
        model_output = await self.call_agent_model(user_message, file_summary)
        try:
            _lineaje_obs = _lineaje_load_gr_client()
            _lineaje_obs_site = _lineaje_obs.SiteDescriptor(site_id='site:sha256:c09193ad574e00680a378070aac92f280248e2441a2c3464c7c971d92b04730f', phase='', boundary={}, fail_mode='ALLOW', source_type='llm', destination_type='agent', project='tree', organization='', components={'file': 'backend/agents/loan_processing_agent.py', 'line': 51, 'function': 'handle', 'agent_name': 'LoanProcessingAgent', 'agent_name_source': 'inferred_from_class', 'call_target': 'self.call_agent_model', 'not_on_graph': True}, observe_only=True, interaction_id=locals().get('_lineaje_interaction_id'))
            await __import__('asyncio').to_thread(lambda: _lineaje_obs.enforce(_lineaje_obs_site, {'activity': 'llm_to_agent'}, content_type='application/json'))
        except Exception:
            pass

        try:
            _lineaje_obs = _lineaje_load_gr_client()
            _lineaje_obs_site = _lineaje_obs.SiteDescriptor(site_id='site:sha256:9a914aa923659d3e8dcd01738d4e5cdbec6daeb6bd9c211acf1a9fba01417c6c', phase='', boundary={}, fail_mode='ALLOW', source_type='agent', destination_type='tool', project='tree', organization='', components={'file': 'backend/agents/loan_processing_agent.py', 'line': 54, 'function': 'handle', 'agent_name': 'LoanProcessingAgent', 'agent_name_source': 'inferred_from_class', 'call_target': 'call_mcp_server', 'source': {'entity_type': 'agent', 'file_path': 'backend/agents/loan_processing_agent.py', 'line': 11, 'name': 'LoanProcessingAgent', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'identity': {'app': {'name': 'acme_loan_processor', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo', 'version': 'main'}, 'destination': {'entity_type': 'mcpserver', 'name': 'docx', 'purl': 'pkg:mcpserver/docx@create_document', 'version': 'create_document'}, 'source': {'entity_type': 'aiagent', 'name': 'LoanProcessingAgent', 'purl': 'pkg:aiagent/LoanProcessingAgent@1.0.0', 'version': '1.0.0'}}, 'invocation': {'file': 'backend/agents/loan_processing_agent.py', 'function': 'LoanProcessingAgent.handle', 'line': 54}, 'destination': {'entity_type': 'mcp_server', 'file_path': 'backend/agents/loan_processing_agent.py', 'line': 54, 'name': 'docx', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'boundary_id': 'bnd:7dbb2892dd1cf725'}, observe_only=True)
            await __import__('asyncio').to_thread(lambda: _lineaje_obs.enforce(_lineaje_obs_site, {'activity': 'tool_call'}, content_type='application/json'))
        except Exception:
            pass
        mcp_activity = await asyncio.gather(
            call_mcp_server(
                self.to_dict(),
                "Docx",
                "create_document",
                {
                    "document_title": f"Loan Intake Summary {loan_number}",
                    "document_body": f"User message:\n{user_message}\n\nFile summary:\n{file_summary}",
                },
            ),
            call_mcp_server(
                self.to_dict(),
                "Excel",
                "upsert_row",
                {
                    "workbook": "Loan Pipeline",
                    "worksheet": "Applications",
                    "row": {
                        "loan_number": loan_number,
                        "status": "processing",
                        "borrower_request": user_message[:240],
                    },
                },
            ),
            call_mcp_server(
                self.to_dict(),
                "Email",
                "send_email",
                {
                    "to": ["borrower@acme.example"],
                    "subject": f"Loan update for {loan_number}",
                    "body": "Your loan request is being reviewed by the Loan Processing Agent.",
                },
            ),
        )
        # LINEAJE: enforce() `mcp_activity` at tool->agent post_tool — this payload crossed a trust boundary with no runtime policy check. Mask/block; do not remove without review. site_id='site:sha256:567659c7a0a1f81d40bcd0aa50950848dae135d212c232f61407810457bdc1f3'
        _gr_client = _lineaje_load_gr_client()
        _gr_site = _gr_client.SiteDescriptor(site_id='site:sha256:567659c7a0a1f81d40bcd0aa50950848dae135d212c232f61407810457bdc1f3', phase='post_tool', boundary={'source': 'tool_result', 'sink': 'agent_message'}, fail_mode='ALLOW_WITH_AUDIT', source_type='tool', destination_type='agent', project='tree', organization='', project_name='acme_loan_processor', project_version='main', project_branch='main', components={'source': {'entity_type': 'agent', 'file_path': 'backend/agents/loan_processing_agent.py', 'line': 11, 'name': 'LoanProcessingAgent', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'identity': {'app': {'name': 'acme_loan_processor', 'purl': 'pkg:github/lineaje-sandbox/acme_loan_processor@main?commit-id=77a6406b056fbf32a8b702cd1d392ddb5747ff83&commit-time=2026-10-21%2004%3A27%3A39%20%2B0000&build_file=frontend/package.json&repo_strategy=single-repo', 'version': 'main'}, 'destination': {'entity_type': 'mcpserver', 'name': 'docx', 'purl': 'pkg:mcpserver/docx@create_document', 'version': 'create_document'}, 'source': {'entity_type': 'aiagent', 'name': 'LoanProcessingAgent', 'purl': 'pkg:aiagent/LoanProcessingAgent@1.0.0', 'version': '1.0.0'}}, 'invocation': {'file': 'backend/agents/loan_processing_agent.py', 'function': 'LoanProcessingAgent.handle', 'line': 54}, 'destination': {'entity_type': 'mcp_server', 'file_path': 'backend/agents/loan_processing_agent.py', 'line': 54, 'name': 'docx', 'repository_uri': 'https://github.com/lineaje-sandbox/acme_loan_processor', 'unique_org_id': 'vdna_gPB2Lr6M2vuoQA3f'}, 'file': 'backend/agents/loan_processing_agent.py', 'line': 53, 'function': 'handle', 'agent_name': 'LoanProcessingAgent', 'agent_name_source': 'inferred_from_class', 'boundary_id': 'bnd:7dbb2892dd1cf725'})
        try:
            mcp_activity = _gr_client.enforce(_gr_site, mcp_activity, content_type='application/json', variable_name='mcp_activity', source_file=__file__, before_line=53)
        except _gr_client.GuardrailUnavailableError:
            pass

        response = (
            "This scan-only agent is disconnected from the Orchestrator Agent.\n\n"
            f"Loan reference: {loan_number}\n"
            f"Borrower request: {user_message or 'No user message provided.'}\n\n"
            f"Loan summary:\n{model_output}"
        )

        return {
            "response": response,
            "agent": self.AGENT_NAME,
            "model": self.MODEL_NAME,
            "framework": self.FRAMEWORK_NAME,
            "mcp_activity": mcp_activity,
        }


loan_processing_agent = LoanProcessingAgent()
