---
name: rag-document-ingestion
description: Normalize, deduplicate, clean, redact, and structure enterprise documents before RAG ingestion. Use when Codex or another Agent needs to process PDF, DOCX, TXT, Markdown, email, chat-like text, logs, or exported HTML into Markdown plus metadata, or when an MCP-aware client should call DocFlow Studio tools for secure preprocessing.
---

# RAG Document Ingestion

Use DocFlow Studio when raw enterprise content must be transformed into safe, standardized RAG input.

## Inputs

- Local file paths or directory paths containing supported files: `.pdf`, `.docx`, `.doc`, `.txt`, `.md`, `.markdown`, `.eml`, `.msg`, `.html`, `.htm`, `.log`
- Optional `tenant_id`
- Optional batch list of mixed paths

## Outputs

- Redacted Markdown text
- Metadata with `document_id`, `source`, `doc_type`, `language`, `tenant_id`, `checksum`, `dedup_status`, `sensitive_fields`, `processing_steps`, `created_at`, `updated_at`, `chunk_info`, `quality_score`
- Dedup relations and cleaning actions
- Sensitive-field audit entries
- Output files under `data/output/<tenant_id>/<document_id>/`

## Preferred Invocation

1. Start the local MCP server with `docflow-mcp` when the client supports MCP stdio tools.
2. Call `process_document` for one file or `process_batch` for multiple files or directories.
3. Call `get_job_status` after a batch run when you need per-document summaries.
4. Call `get_document_result` when you need the final Markdown, metadata, and audit payload for a specific processed document.

## MCP Tools

### `process_document`

Use for one local file path.

Parameters:
- `path`: absolute or repo-relative local file path
- `tenant_id`: optional tenant identifier; defaults to `demo-tenant`

Returns:
- `ok`
- `document_id`
- `dedup_status`
- `quality_score`
- `sensitive_fields`
- `markdown_path`
- `result_json_path`
- `metadata`

### `process_batch`

Use for multiple local files or directories.

Parameters:
- `paths`: list of local file or directory paths
- `tenant_id`: optional tenant identifier

Returns:
- `ok`
- `job`
- `documents`

### `get_job_status`

Use to poll or inspect a prior batch run.

Parameters:
- `job_id`

Returns:
- `ok`
- `job`
- `documents`

### `get_document_result`

Use to load the final processed artifact.

Parameters:
- `document_id`

Returns:
- `ok`
- `document`

## Error Handling

Handle these error codes explicitly:

- `DOC_NOT_FOUND`: input file path does not exist
- `JOB_NOT_FOUND`: requested job id does not exist
- `DOC_RESULT_NOT_FOUND`: processed result does not exist

If a batch contains unsupported files, submit only supported document types. If a directory is empty after filtering, choose another directory or expand the file list explicitly.

## Best Practices

- Prefer directory-level batch calls for mailbox exports, daily report drops, or log archives.
- Keep tenant boundaries explicit so deduplication only compares documents inside the same tenant.
- Review `dedup_status` before embedding results. `exact_duplicate` and `near_duplicate` usually mean the artifact should not be re-indexed as a primary source.
- Use `quality_score` to route low-confidence outputs into manual review.
- Persist the returned metadata alongside vector-store ingestion logs for auditability.

## Limitations

- `.doc` support depends on the file being parseable by the installed Word parser stack; `.docx` is the primary path.
- Name detection is deterministic and label-driven by default. Free-form person-name recognition without nearby field labels should be treated as best-effort.
- The built-in queue is SQLite-backed for local and single-node deployments. Replace it with an external queue and database for high-throughput distributed production.

