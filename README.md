# DocFlow Studio

DocFlow Studio is an enterprise-ready document ingestion and preprocessing platform for RAG and knowledge-base pipelines. It normalizes heterogeneous raw documents, removes duplicates, cleans noise, redacts sensitive data, and emits structured Markdown plus machine-readable metadata that downstream vector stores and enterprise agents can consume safely.

The repository ships with:

- A Python processing engine with pluggable parsers, cleaners, deduplication, redaction, chunking, and scoring
- A FastAPI service with job orchestration, retries, persistence, and result browsing
- An MCP server for agent-native invocation
- A modern React UI served by the API and wrapped into a Windows desktop launcher
- Build scripts, sample data, tests, and an Agent-oriented skill

See [docs/solution-overview.md](docs/solution-overview.md) for the architecture and [skills/rag-document-ingestion/SKILL.md](skills/rag-document-ingestion/SKILL.md) for the Agent skill.

