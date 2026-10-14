<!-- jr-brand:start -->
<p align="center">
  <a href="https://jannikreinhard.com/">
    <img src="https://raw.githubusercontent.com/JayRHa/.github/main/assets/readme/brand-header.png" alt="Jannik Reinhard — I help enterprises ship secure AI agents" width="100%">
  </a>
</p>
<p align="center">
  <a href="https://jannikreinhard.com/">Website</a> ·
  <a href="https://www.linkedin.com/in/jannik-r/">LinkedIn</a> ·
  <a href="https://x.com/jannik_reinhard">X</a> ·
  <a href="https://www.youtube.com/@jannikreinhard">YouTube</a>
</p>
<!-- jr-brand:end -->

# Foundry IQ toolkit

**Type:** Tool or application · **Status:** Community project

## Overview

CLI for Foundry IQ: create knowledge sources and knowledge bases on Azure AI Search, test agentic retrieval, and wire them into Microsoft Foundry agents via MCP.

A small CLI for **Foundry IQ** — create knowledge sources and knowledge bases
on Azure AI Search, test agentic retrieval from the terminal, and print the
MCP endpoint you need to wire the knowledge base into a Microsoft Foundry agent.

Foundry IQ turns your data into reusable, permission-aware knowledge bases
that any number of agents can share. The plumbing is a handful of REST calls —
this toolkit wraps them so you can go from a blob container to a queryable
knowledge base in minutes.

<a id="prerequisites"></a>

## Requirements

- Python 3.10+
- An **Azure AI Search** service (Basic tier or higher recommended)
- An **Azure OpenAI / Foundry** resource with an embedding deployment
  (e.g. `text-embedding-3-large`) and a chat deployment for query planning
- `az login` (the CLI uses `DefaultAzureCredential`)
- Roles: **Search Service Contributor** on the search service for you; the
  search service managed identity needs **Cognitive Services User** on the
  Foundry resource

## Quickstart

```bash
git clone https://github.com/JayRHa/foundry-iq-toolkit.git
cd foundry-iq-toolkit
pip install -r requirements.txt
cp .env.example .env   # fill in endpoints

# 1. knowledge source from a blob container (index pipeline is auto-generated)
python foundry_iq.py create-source docs-src \
  --connection "ResourceId=/subscriptions/.../storageAccounts/mydocs" \
  --container documents

# 2. knowledge base on top
python foundry_iq.py create-kb my-kb --sources docs-src \
  --instructions "Use docs-src for product and process questions."

# 3. ask it something
python foundry_iq.py retrieve my-kb "How do we onboard a new device?"

# 4. wire it into an agent
python foundry_iq.py mcp-endpoint my-kb
```

## What It Does

```text
foundry_iq.py create-source   Create a blob knowledge source (auto chunking + vectorization)
foundry_iq.py create-kb       Create a knowledge base over one or more sources
foundry_iq.py retrieve        Ask a question against the knowledge base (agentic retrieval)
foundry_iq.py status          Show ingestion status of a knowledge source
foundry_iq.py mcp-endpoint    Print the MCP endpoint + agent wiring snippet
foundry_iq.py list            List knowledge sources and knowledge bases
```

## How the Pieces Fit

1. A **knowledge source** ingests your data into a search index (chunking,
   vectorization and refresh handled by the generated pipeline).
2. A **knowledge base** bundles sources plus retrieval settings — reasoning
   effort (`minimal` / `low` / `medium`), output mode (extractive chunks or a
   synthesized answer) and retrieval instructions for the query planner.
3. Agents call the knowledge base through its **MCP endpoint** with the single
   tool `knowledge_base_retrieve` — from Foundry Agent Service, the Agent
   Framework, or any MCP-capable client.

## Cost Notes

Agentic retrieval bills reranking tokens on Azure AI Search plus LLM tokens
for query planning / answer synthesis. Biggest lever is the reasoning effort:
`minimal` skips the LLM entirely. Use `--effort minimal` while you iterate.

## API version

The toolkit pins `2026-05-01-preview` (query planning, answer synthesis and
reasoning effort need the preview API; the GA API `2026-04-01` only covers the
minimal extractive setup). Override with `SEARCH_API_VERSION` in `.env`.

## Related

- Blog: [jannikreinhard.com](https://jannikreinhard.com) — Foundry IQ deep dive
- [Foundry IQ documentation](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-foundry-iq)
- [Agentic retrieval in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-overview)

## Disclaimer

Community tooling, not an official Microsoft project. Preview APIs move —
check the pinned api-version if a call starts failing.

## License

MIT — see [LICENSE](LICENSE).

<!-- jr-brand-footer:start -->
---

[Articles and guides](https://jannikreinhard.com/) · [Repository index](https://github.com/JayRHa/.github/blob/main/REPOSITORIES.md)
<!-- jr-brand-footer:end -->
