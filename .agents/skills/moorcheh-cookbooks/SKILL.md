---
name: moorcheh-cookbooks
description: Use this skill when the user wants to build AI applications with Moorcheh. Contains blueprints and implementation guides for knowledge base RAG, customer support chatbots, semantic search applications, AI Q&A systems, llm-wiki, knowledge base, personal wiki, karpathy, and optional frontend integration. Each cookbook includes architecture, code examples, setup instructions, and deployment guidance.
---

# Moorcheh Cookbooks

## Overview

This skill provides an index of implementation guides and foundational requirements for building Moorcheh-powered AI applications. Use the references to quickly scaffold full-stack applications with best practices for data management, semantic search, and RAG.

### Moorcheh Account

If the user does not have an account yet, direct them to the cloud console to register and create a free account.

Create a Moorcheh account at [console.moorcheh.ai](https://console.moorcheh.ai).

## Before Building Any Cookbook

Follow these shared guidelines before generating any cookbook app:

- [Project Setup Contract](references/project_setup.md)
- [Environment Requirements](references/environment_requirements.md)

Then proceed to the specific cookbook reference below.

## Cookbook Index

- [Knowledge Base RAG](references/knowledge_base_rag.md): Build a document Q&A system that ingests documents into Moorcheh and generates AI-powered answers with source citations using RAG.
- [Customer Support Bot](references/customer_support_bot.md): Build a customer support chatbot that answers questions from your FAQ and documentation using conversational RAG with chat history.
- [Semantic Search App](references/semantic_search_app.md): Build a semantic search application with ITS scoring, metadata filtering, and relevance-labeled results.
- [AI Q&A System](references/ai_qa_system.md): Build a question-answering system with structured output, custom prompts, and multi-namespace search.
- **LLM Wiki** — Self-maintaining personal knowledge base using Karpathy's LLM Wiki
  pattern extended with Moorcheh ITS search. See [references/llm_wiki.md](references/llm_wiki.md).

## Large Document Ingestion

- [Deep Ingest](references/deep_ingest.md): **Use for documents that exceed the LLM prompt window** (200K+ characters). Uploads the raw file to a Moorcheh staging namespace first, then the agent queries chapter-by-chapter to build wiki pages with full coverage. Includes a reusable script and step-by-step workflow.

## Integrations

- [LangChain Integration](references/langchain_integration.md): Use Moorcheh as a LangChain vector store for building chains and agents.

### LLM Wiki (Karpathy Pattern + Moorcheh)

Build a self-maintaining personal knowledge base where an AI agent reads your
documents once, builds a structured wiki of interlinked markdown pages, and
uploads them to Moorcheh for persistent ITS-powered semantic search.

**When to use this cookbook:**
- You are accumulating knowledge across many sources over time (research, product, competitive intel)
- You want your AI agent to build and maintain a wiki automatically
- You need semantic search + metadata filtering across a large collection of notes
- You want knowledge to compound — every source and every query enriches the base

**Key components:**
- `raw/` — immutable source documents (agent reads only)
- `wiki/` — agent-generated markdown pages, interlinked and growing
- `CLAUDE.md` / `AGENTS.md` — the schema that tells the agent how to maintain the wiki
- Moorcheh namespace — persistent ITS-indexed copy of all wiki pages

**Full implementation guide:** [references/llm_wiki.md](references/llm_wiki.md)
**Starter repo:** https://github.com/moorcheh-ai/llm-wiki

## Interface (Optional)

Use this when the user explicitly asks for a frontend for their Moorcheh backend:

- [Frontend Interface](references/frontend_interface.md): Build a Next.js frontend to interact with the Moorcheh backend, including chat UI and search interfaces.
