# Solution Overview

## Positioning

DocFlow Studio handles the ingestion side of enterprise RAG pipelines. It accepts raw documents from mixed business systems, normalizes them into a common intermediate representation, removes duplicates, cleans noise, redacts sensitive data, and emits structured Markdown plus metadata for downstream embedding and retrieval flows.

## Architecture

1. `docflow.core`
   - Parser registry for PDF, DOCX, TXT, Markdown, HTML, EML, chat-style text, and logs
   - Cleaner strategies for global and document-type-specific cleanup
   - Dedup engine with exact fingerprinting and near-duplicate detection
   - Redaction engine with configurable detection rules and audit output
   - Chunking and quality scoring

2. `docflow.services`
   - Pipeline coordinator
   - Storage and export services
   - Job management and dashboard aggregation

3. `docflow.db`
   - SQLite persistence for jobs and processed documents
   - Retry-aware state transitions and result indexing

4. `docflow.api`
   - FastAPI app for operators and system-to-system integration

5. `docflow.mcp`
   - MCP tools for agent-native invocation from Codex, OpenClaw, and other MCP-aware clients

6. `frontend`
   - React dashboard for batch intake, job monitoring, result inspection, and audit review

7. `desktop`
   - pywebview launcher that starts the local API and opens a desktop window

## Data Flow

1. Intake
   - Operator uploads files or points to a folder
   - API stores inputs into runtime staging and creates a job record

2. Parse and Normalize
   - Parser converts raw content into a normalized document model with segments and source metadata

3. Clean
   - Common and type-specific cleaners remove noise while keeping semantic structure

4. Deduplicate
   - Exact checks compare checksums and normalized hashes
   - Near-duplicate checks compare simhash signatures and segment fingerprints
   - Pipeline emits relation and retention metadata

5. Redact
   - Configurable rules replace sensitive entities and produce an audit trail

6. Structure and Score
   - Markdown output and chunk metadata are generated
   - Quality score is computed for downstream routing

7. Persist and Export
   - Results are written to JSON and Markdown files
   - Job and document summaries are indexed in SQLite

## Trade-offs and Assumptions

- The default build uses a single-node SQLite-backed worker model instead of Redis plus Celery to keep the desktop and local deployment path simple. The service boundaries and repository abstractions make it straightforward to swap in Postgres and an external queue later.
- The built-in redaction engine emphasizes deterministic enterprise-safe rules. Optional ML/NER integration is intentionally left as a plugin point rather than a hard dependency.
- The EXE packaging path targets Windows first because the requested deliverable is a directly executable desktop application.

