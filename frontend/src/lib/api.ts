export type JobSummary = {
  job_id: string;
  tenant_id: string;
  status: string;
  source_count: number;
  processed_count: number;
  failed_count: number;
  created_at: string;
  updated_at: string;
  errors: string[];
};

export type DashboardSummary = {
  total_jobs: number;
  completed_jobs: number;
  total_documents: number;
  duplicate_documents: number;
  redacted_documents: number;
  average_quality_score: number;
  last_updated_at: string;
};

export type DocumentSummary = {
  document_id: string;
  job_id: string;
  tenant_id: string;
  source: string;
  filename: string;
  doc_type: string;
  language: string;
  dedup_status: string;
  quality_score: number;
  sensitive_fields: string[];
  created_at: string;
  updated_at: string;
};

export type DocumentDetail = DocumentSummary & {
  markdown_text: string;
  metadata: Record<string, unknown>;
  audit: {
    cleaning_actions: { action: string; detail: string; count: number }[];
    dedup_relations: { relation_type: string; reason: string; similarity: number }[];
    sensitive_matches: { field_type: string; rule_id: string; placeholder: string; original_excerpt: string }[];
    warnings: string[];
    errors: string[];
  };
};

export type ExportResult = {
  exported_count: number;
  files: {
    document_id: string;
    filename: string;
    path: string;
    format: string;
    bytes: number;
  }[];
};

const JSON_HEADERS = {
  "Content-Type": "application/json"
};

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(error?.detail?.message || error?.message || "Request failed");
  }
  return response.json() as Promise<T>;
}

export async function fetchSummary(): Promise<DashboardSummary> {
  return parseJson<DashboardSummary>(await fetch("/api/dashboard/summary"));
}

export async function fetchJobs(): Promise<JobSummary[]> {
  return parseJson<JobSummary[]>(await fetch("/api/jobs"));
}

export async function fetchJobDocuments(jobId: string): Promise<DocumentSummary[]> {
  return parseJson<DocumentSummary[]>(await fetch(`/api/jobs/${jobId}/documents`));
}

export async function fetchDocument(documentId: string): Promise<DocumentDetail> {
  return parseJson<DocumentDetail>(await fetch(`/api/documents/${documentId}`));
}

export async function submitPaths(paths: string[], tenantId: string): Promise<JobSummary> {
  return parseJson<JobSummary>(
    await fetch("/api/jobs/process-paths", {
      method: "POST",
      headers: JSON_HEADERS,
      body: JSON.stringify({ tenant_id: tenantId, paths })
    })
  );
}

export async function submitUploads(files: File[], tenantId: string): Promise<JobSummary> {
  const formData = new FormData();
  formData.append("tenant_id", tenantId);
  files.forEach((file) => formData.append("files", file, file.name));
  return parseJson<JobSummary>(
    await fetch("/api/jobs/upload", {
      method: "POST",
      body: formData
    })
  );
}

export async function exportDocument(
  documentId: string,
  targetDir: string,
  outputFormat: "md" | "txt"
): Promise<ExportResult> {
  return parseJson<ExportResult>(
    await fetch(`/api/documents/${documentId}/export`, {
      method: "POST",
      headers: JSON_HEADERS,
      body: JSON.stringify({ target_dir: targetDir, output_format: outputFormat })
    })
  );
}

export async function exportJob(
  jobId: string,
  targetDir: string,
  outputFormat: "md" | "txt"
): Promise<ExportResult> {
  return parseJson<ExportResult>(
    await fetch(`/api/jobs/${jobId}/export`, {
      method: "POST",
      headers: JSON_HEADERS,
      body: JSON.stringify({ target_dir: targetDir, output_format: outputFormat })
    })
  );
}
