import { useEffect, useMemo, useState } from "react";
import { DocumentPanel } from "./components/DocumentPanel";
import { ExportModal } from "./components/ExportModal";
import { JobsPanel } from "./components/JobsPanel";
import { MenuBar } from "./components/MenuBar";
import { MetricCard } from "./components/MetricCard";
import { TutorialModal } from "./components/TutorialModal";
import { UploadPanel } from "./components/UploadPanel";
import {
  DashboardSummary,
  DocumentDetail,
  DocumentSummary,
  ExportResult,
  JobSummary,
  exportDocument,
  exportJob,
  fetchDocument,
  fetchJobDocuments,
  fetchJobs,
  fetchSummary,
  submitPaths,
  submitUploads
} from "./lib/api";
import { Language, copy } from "./lib/i18n";

const emptySummary: DashboardSummary = {
  total_jobs: 0,
  completed_jobs: 0,
  total_documents: 0,
  duplicate_documents: 0,
  redacted_documents: 0,
  average_quality_score: 0,
  last_updated_at: new Date().toISOString()
};

export default function App() {
  const [language, setLanguage] = useState<Language>("zh");
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [summary, setSummary] = useState<DashboardSummary>(emptySummary);
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [documentDetail, setDocumentDetail] = useState<DocumentDetail | null>(null);
  const [message, setMessage] = useState<string>(copy.zh.app.ready);
  const [busy, setBusy] = useState(false);
  const [tutorialOpen, setTutorialOpen] = useState(false);
  const [exportScope, setExportScope] = useState<"job" | "document">("job");
  const [exportOpen, setExportOpen] = useState(false);

  const t = copy[language];

  async function refreshDashboard() {
    const [dashboardSummary, latestJobs] = await Promise.all([fetchSummary(), fetchJobs()]);
    setSummary(dashboardSummary);
    setJobs(latestJobs);
    if (!selectedJobId && latestJobs.length > 0) {
      setSelectedJobId(latestJobs[0].job_id);
    }
  }

  useEffect(() => {
    void refreshDashboard();
    const timer = window.setInterval(() => {
      void refreshDashboard();
    }, 4000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  useEffect(() => {
    if (!selectedJobId) {
      return;
    }
    setDocuments([]);
    setDocumentDetail(null);
    setSelectedDocumentId(null);
    fetchJobDocuments(selectedJobId)
      .then((items) => {
        setDocuments(items);
        if (items.length > 0) {
          setSelectedDocumentId(items[0].document_id);
        } else {
          setSelectedDocumentId(null);
          setDocumentDetail(null);
        }
      })
      .catch((error: Error) => setMessage(error.message));
  }, [selectedJobId]);

  useEffect(() => {
    if (!selectedDocumentId) {
      return;
    }
    setDocumentDetail(null);
    fetchDocument(selectedDocumentId)
      .then((detail) => setDocumentDetail(detail))
      .catch((error: Error) => setMessage(error.message));
  }, [selectedDocumentId]);

  async function handleUpload(files: File[], tenantId: string) {
    setBusy(true);
    try {
      const job = await submitUploads(files, tenantId);
      setMessage(`${t.app.uploadCreated}: ${job.job_id}`);
      setSelectedJobId(job.job_id);
      await refreshDashboard();
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function handleSubmitPaths(paths: string[], tenantId: string) {
    setBusy(true);
    try {
      const job = await submitPaths(paths, tenantId);
      setMessage(`${t.app.pathCreated}: ${job.job_id}`);
      setSelectedJobId(job.job_id);
      await refreshDashboard();
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const qualityBand = useMemo(() => {
    if (summary.average_quality_score >= 90) {
      return t.metrics.high;
    }
    if (summary.average_quality_score >= 75) {
      return t.metrics.good;
    }
    return t.metrics.review;
  }, [summary.average_quality_score, t.metrics.good, t.metrics.high, t.metrics.review]);

  function openExport(scope: "job" | "document") {
    setExportScope(scope);
    setExportOpen(true);
  }

  async function handleExport(
    scope: "job" | "document",
    targetDir: string,
    outputFormat: "md" | "txt"
  ) {
    if (!targetDir.trim()) {
      setMessage(t.export.noTarget);
      return;
    }
    let result: ExportResult;
    if (scope === "job") {
      if (!selectedJobId) {
        setMessage(t.export.noJob);
        return;
      }
      result = await exportJob(selectedJobId, targetDir, outputFormat);
    } else {
      if (!selectedDocumentId) {
        setMessage(t.export.noDocument);
        return;
      }
      result = await exportDocument(selectedDocumentId, targetDir, outputFormat);
    }
    setMessage(`${t.app.exported}: ${result.exported_count}`);
  }

  return (
    <div className="app-shell">
      <MenuBar
        language={language}
        theme={theme}
        onLanguageChange={setLanguage}
        onThemeToggle={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
        onTutorial={() => setTutorialOpen(true)}
        onExportJob={() => openExport("job")}
        onExportDocument={() => openExport("document")}
      />

      <header className="hero">
        <div className="hero-copy">
          <span className="eyebrow">{t.app.eyebrow}</span>
          <h1>{t.app.title}</h1>
          <p>{t.app.subtitle}</p>
        </div>
        <div className="hero-note">
          <strong>{t.app.status}</strong>
          <span>{message}</span>
          <span>{t.app.refresh}: {new Date(summary.last_updated_at).toLocaleString()}</span>
        </div>
      </header>

      <section className="metrics-grid">
        <MetricCard
          label={t.metrics.documents}
          value={summary.total_documents}
          helper={t.metrics.documentsHelp}
          accent="linear-gradient(135deg, #185adb, #38bdf8)"
        />
        <MetricCard
          label={t.metrics.duplicates}
          value={summary.duplicate_documents}
          helper={t.metrics.duplicatesHelp}
          accent="linear-gradient(135deg, #f97316, #facc15)"
        />
        <MetricCard
          label={t.metrics.redacted}
          value={summary.redacted_documents}
          helper={t.metrics.redactedHelp}
          accent="linear-gradient(135deg, #ef4444, #fb7185)"
        />
        <MetricCard
          label={t.metrics.avgQuality}
          value={summary.average_quality_score}
          helper={qualityBand}
          accent="linear-gradient(135deg, #10b981, #34d399)"
        />
      </section>

      <UploadPanel
        busy={busy}
        onUpload={handleUpload}
        onSubmitPaths={handleSubmitPaths}
        defaultTenantId="demo-tenant"
        labels={t.upload}
      />

      <JobsPanel
        jobs={jobs}
        selectedJobId={selectedJobId}
        onSelect={setSelectedJobId}
        labels={t.jobs}
      />

      <DocumentPanel
        documents={documents}
        selectedDocumentId={selectedDocumentId}
        documentDetail={documentDetail}
        onSelect={setSelectedDocumentId}
        labels={t.docs}
      />

      {tutorialOpen ? (
        <TutorialModal language={language} onClose={() => setTutorialOpen(false)} />
      ) : null}
      {exportOpen ? (
        <ExportModal
          language={language}
          initialScope={exportScope}
          onClose={() => setExportOpen(false)}
          onExport={handleExport}
        />
      ) : null}
    </div>
  );
}
