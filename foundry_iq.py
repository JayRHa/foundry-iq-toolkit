#!/usr/bin/env python3
"""foundry-iq-toolkit: manage Foundry IQ knowledge sources and knowledge bases.

Thin wrapper around the Azure AI Search knowledge base REST API
(agentic retrieval). Auth via DefaultAzureCredential (run `az login`).
"""
import argparse
import json
import os
import sys

import requests
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

SEARCH_ENDPOINT = os.environ.get("SEARCH_ENDPOINT", "").rstrip("/")
API_VERSION = os.environ.get("SEARCH_API_VERSION", "2026-05-01-preview")
AOAI_RESOURCE = os.environ.get("AOAI_RESOURCE_URI", "").rstrip("/")
EMBEDDING_DEPLOYMENT = os.environ.get("EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
CHAT_DEPLOYMENT = os.environ.get("CHAT_DEPLOYMENT", "gpt-5-mini")

_credential = DefaultAzureCredential()


def _headers() -> dict:
    token = _credential.get_token("https://search.azure.com/.default").token
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _call(method: str, path: str, body: dict | None = None) -> dict:
    if not SEARCH_ENDPOINT:
        sys.exit("SEARCH_ENDPOINT is not set - copy .env.example to .env first.")
    url = f"{SEARCH_ENDPOINT}/{path}?api-version={API_VERSION}"
    resp = requests.request(method, url, headers=_headers(), json=body, timeout=120)
    if resp.status_code >= 300:
        sys.exit(f"{method} {path} -> HTTP {resp.status_code}\n{resp.text}")
    return resp.json() if resp.text else {}


def _aoai_model(deployment: str) -> dict:
    return {
        "kind": "azureOpenAI",
        "azureOpenAIParameters": {
            "resourceUri": AOAI_RESOURCE,
            "deploymentId": deployment,
            "modelName": deployment,
        },
    }


# ---------------- commands ----------------

def cmd_create_source(args) -> None:
    """Blob knowledge source; index/skillset/indexer are auto-generated."""
    body = {
        "name": args.name,
        "kind": "azureBlob",
        "description": args.description or f"Blob source for container {args.container}",
        "azureBlobParameters": {
            "connectionString": args.connection,
            "containerName": args.container,
            "ingestionParameters": {
                "embeddingModel": _aoai_model(EMBEDDING_DEPLOYMENT),
                "chatCompletionModel": _aoai_model(CHAT_DEPLOYMENT),
                "contentExtractionMode": "minimal",
            },
        },
    }
    result = _call("PUT", f"knowledgesources/{args.name}", body)
    print(f"knowledge source '{args.name}' created/updated")
    created = result.get("createdResources") or {}
    if created:
        print("auto-generated pipeline objects:")
        for k, v in created.items():
            print(f"  {k}: {v}")


def cmd_create_kb(args) -> None:
    body = {
        "name": args.name,
        "knowledgeSources": [{"name": s} for s in args.sources],
        "retrievalReasoningEffort": {"kind": args.effort},
    }
    if args.instructions:
        body["retrievalInstructions"] = args.instructions
    if args.answers:
        body["outputMode"] = "answerSynthesis"
        body["models"] = [_aoai_model(CHAT_DEPLOYMENT)]
    _call("PUT", f"knowledgebases/{args.name}", body)
    mode = "answer synthesis" if args.answers else "extractive"
    print(f"knowledge base '{args.name}' created/updated "
          f"(effort={args.effort}, output={mode}, sources={', '.join(args.sources)})")


def cmd_retrieve(args) -> None:
    body = {
        "messages": [{"role": "user", "content": [{"type": "text", "text": args.question}]}],
        "includeReferences": True,
    }
    result = _call("POST", f"knowledgebases/{args.kb}/retrieve", body)
    for item in result.get("response", []):
        for part in item.get("content", []):
            print(part.get("text", ""))
    refs = result.get("references") or []
    if refs:
        print(f"\n{len(refs)} references:")
        for r in refs[: args.max_refs]:
            print(f"  - {r.get('sourceData', {}).get('title') or r.get('docKey') or r.get('id')}")
    activity = result.get("activity") or []
    if args.verbose and activity:
        print("\nactivity log:")
        print(json.dumps(activity, indent=2))


def cmd_status(args) -> None:
    result = _call("GET", f"knowledgesources/{args.name}/status")
    state = result.get("lastSynchronizationState") or {}
    print(f"kind:   {result.get('kind')}")
    print(f"status: {state.get('status', 'unknown')}")
    stats = result.get("statistics") or state.get("statistics")
    if stats:
        print(json.dumps(stats, indent=2))


def cmd_mcp_endpoint(args) -> None:
    endpoint = f"{SEARCH_ENDPOINT}/knowledgebases/{args.kb}/mcp?api-version={API_VERSION}"
    print("MCP endpoint (tool: knowledge_base_retrieve):")
    print(f"  {endpoint}\n")
    print("Foundry agent wiring (azure-ai-projects >= 2.0.0):\n")
    print(f'''    mcp_kb_tool = MCPTool(
        server_label="knowledge-base",
        server_url="{endpoint}",
        require_approval="never",
        allowed_tools=["knowledge_base_retrieve"],
        project_connection_id="<your RemoteTool connection>")''')
    print("\nNote: the project connection needs authType ProjectManagedIdentity with")
    print('audience "https://search.azure.com/", and the project managed identity')
    print("needs Search Index Data Reader on the search service.")


def cmd_list(args) -> None:
    for kind, path in [("knowledge sources", "knowledgesources"), ("knowledge bases", "knowledgebases")]:
        result = _call("GET", path)
        items = result.get("value", [])
        print(f"{kind} ({len(items)}):")
        for item in items:
            print(f"  - {item['name']}  [{item.get('kind', 'kb')}]")


def main() -> None:
    p = argparse.ArgumentParser(description="Manage Foundry IQ knowledge bases on Azure AI Search")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("create-source", help="create a blob knowledge source")
    s.add_argument("name")
    s.add_argument("--connection", required=True,
                   help='blob connection, e.g. "ResourceId=/subscriptions/.../storageAccounts/x"')
    s.add_argument("--container", required=True)
    s.add_argument("--description")
    s.set_defaults(fn=cmd_create_source)

    s = sub.add_parser("create-kb", help="create a knowledge base")
    s.add_argument("name")
    s.add_argument("--sources", nargs="+", required=True)
    s.add_argument("--instructions", help="routing hints for the query planner")
    s.add_argument("--effort", choices=["minimal", "low", "medium"], default="low")
    s.add_argument("--answers", action="store_true",
                   help="enable answer synthesis (default: extractive chunks)")
    s.set_defaults(fn=cmd_create_kb)

    s = sub.add_parser("retrieve", help="query a knowledge base")
    s.add_argument("kb")
    s.add_argument("question")
    s.add_argument("--max-refs", type=int, default=10)
    s.add_argument("--verbose", action="store_true", help="print the activity log")
    s.set_defaults(fn=cmd_retrieve)

    s = sub.add_parser("status", help="ingestion status of a knowledge source")
    s.add_argument("name")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("mcp-endpoint", help="print MCP endpoint + agent wiring snippet")
    s.add_argument("kb")
    s.set_defaults(fn=cmd_mcp_endpoint)

    s = sub.add_parser("list", help="list knowledge sources and bases")
    s.set_defaults(fn=cmd_list)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
