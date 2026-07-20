<!-- jr-brand:start -->
<div align="center">
  <a href="https://jannikreinhard.com/">
    <img src="https://raw.githubusercontent.com/JayRHa/.github/main/assets/readme/tool.svg" alt="Jannik Reinhard — AI, Cloud and Endpoint Management" width="100%">
  </a>
  <h1>Microsoft Foundry IQ Toolkit</h1>
  <p><strong>CLI for Foundry IQ: create knowledge sources and knowledge bases on Azure AI Search, test agentic retrieval, and wire them into Microsoft Foundry agents via MCP.</strong></p>
  <p>
  <a href="https://jannikreinhard.com/"><img src="https://img.shields.io/badge/Website-0A5FC0?style=flat-square&amp;logo=wordpress&amp;logoColor=white" alt="Website"></a>
  <a href="https://github.com/JayRHa"><img src="https://img.shields.io/badge/GitHub-081427?style=flat-square&amp;logo=github&amp;logoColor=white" alt="GitHub"></a>
  <a href="https://www.linkedin.com/in/jannik-r/"><img src="https://img.shields.io/badge/LinkedIn-0795FF?style=flat-square&amp;logo=linkedin&amp;logoColor=white" alt="LinkedIn"></a>
  <a href="https://x.com/jannik_reinhard"><img src="https://img.shields.io/badge/X-081427?style=flat-square&amp;logo=x&amp;logoColor=white" alt="X"></a>
  <a href="https://www.youtube.com/@ModernDevMgmt/featured"><img src="https://img.shields.io/badge/YouTube-0A5FC0?style=flat-square&amp;logo=youtube&amp;logoColor=white" alt="YouTube"></a>
</p>
  <p><sub>Tool · App · CLI · Python · Practical by design</sub></p>
</div>
<!-- jr-brand:end -->

## Overview

A small CLI for **Foundry IQ** — create knowledge sources and knowledge bases
on Azure AI Search, test agentic retrieval from the terminal, and print the
MCP endpoint you need to wire the knowledge base into a Microsoft Foundry agent.

Foundry IQ turns your data into reusable, permission-aware knowledge bases
that any number of agents can share. The plumbing is a handful of REST calls —
this toolkit wraps them so you can go from a blob container to a queryable
knowledge base in minutes.

## What It Does

```text
foundry_iq.py create-source   Create a blob knowledge source (auto chunking + vectorization)
foundry_iq.py create-kb       Create a knowledge base over one or more sources
foundry_iq.py retrieve        Ask a question against the knowledge base (agentic retrieval)
foundry_iq.py status          Show ingestion status of a knowledge source
foundry_iq.py mcp-endpoint    Print the MCP endpoint + agent wiring snippet
foundry_iq.py list            List knowledge sources and knowledge bases
```

## Prerequisites

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

<div align="center">
  <p><sub>Built and maintained by <a href="https://jannikreinhard.com/">Jannik Reinhard</a> · Microsoft MVP for Security and AI Platform.</sub></p>
  <p><a href="https://www.buymeacoffee.com/jannikreinf">Support the open-source work</a></p>
  <p><strong>Stay healthy, Cheers Jannik</strong></p>
</div>

<!-- jr-brand-footer:end -->
