import { X } from "lucide-react";
import { useState } from "react";
import { Language, copy } from "../lib/i18n";

type ExportScope = "job" | "document";

type ExportModalProps = {
  language: Language;
  initialScope: ExportScope;
  onClose: () => void;
  onExport: (scope: ExportScope, targetDir: string, outputFormat: "md" | "txt") => Promise<void>;
};

export function ExportModal({ language, initialScope, onClose, onExport }: ExportModalProps) {
  const t = copy[language].export;
  const [scope, setScope] = useState<ExportScope>(initialScope);
  const [targetDir, setTargetDir] = useState("");
  const [outputFormat, setOutputFormat] = useState<"md" | "txt">("md");
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true);
    try {
      await onExport(scope, targetDir, outputFormat);
      onClose();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal-panel export-modal">
        <div className="modal-header">
          <h2>{t.title}</h2>
          <button className="icon-button" onClick={onClose} title={copy[language].menu.close}>
            <X size={18} />
          </button>
        </div>
        <div className="field-stack">
          <label className="field">
            <span>{t.scope}</span>
            <select value={scope} onChange={(event) => setScope(event.target.value as ExportScope)}>
              <option value="job">{t.job}</option>
              <option value="document">{t.document}</option>
            </select>
          </label>
          <label className="field">
            <span>{t.target}</span>
            <input
              value={targetDir}
              onChange={(event) => setTargetDir(event.target.value)}
              placeholder={"C:\\Users\\f7897\\Desktop\\RAGWASHER_UAT"}
            />
          </label>
          <label className="field">
            <span>{t.format}</span>
            <select
              value={outputFormat}
              onChange={(event) => setOutputFormat(event.target.value as "md" | "txt")}
            >
              <option value="md">Markdown (.md)</option>
              <option value="txt">Text (.txt)</option>
            </select>
          </label>
          <p className="form-hint">{t.hint}</p>
        </div>
        <div className="modal-actions">
          <button className="secondary-button" onClick={onClose}>
            {t.cancel}
          </button>
          <button onClick={submit} disabled={busy || targetDir.trim().length === 0}>
            {busy ? "..." : t.submit}
          </button>
        </div>
      </div>
    </div>
  );
}
