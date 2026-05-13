import { useState } from "react";

type UploadPanelProps = {
  busy: boolean;
  onUpload: (files: File[], tenantId: string) => Promise<void>;
  onSubmitPaths: (paths: string[], tenantId: string) => Promise<void>;
  defaultTenantId: string;
  labels: {
    title: string;
    description: string;
    tenant: string;
    fileUpload: string;
    accepts: string;
    noFiles: string;
    createUpload: string;
    pathIntake: string;
    pathHelp: string;
    createPath: string;
    submitting: string;
  };
};

export function UploadPanel({
  busy,
  onUpload,
  onSubmitPaths,
  defaultTenantId,
  labels
}: UploadPanelProps) {
  const [tenantId, setTenantId] = useState(defaultTenantId);
  const [pathText, setPathText] = useState("");
  const [files, setFiles] = useState<File[]>([]);

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>{labels.title}</h2>
          <p>{labels.description}</p>
        </div>
      </div>

      <div className="form-grid">
        <label className="field">
          <span>{labels.tenant}</span>
          <input value={tenantId} onChange={(event) => setTenantId(event.target.value)} placeholder="tenant-a" />
        </label>
      </div>

      <div className="upload-grid">
        <div className="dropzone">
          <h3>{labels.fileUpload}</h3>
          <p>{labels.accepts}</p>
          <input
            type="file"
            multiple
            onChange={(event) => setFiles(Array.from(event.target.files || []))}
          />
          <div className="chip-row">
            {files.length === 0 ? <span className="chip muted">{labels.noFiles}</span> : null}
            {files.map((file) => (
              <span key={file.name} className="chip">
                {file.name}
              </span>
            ))}
          </div>
          <button disabled={busy || files.length === 0} onClick={() => onUpload(files, tenantId)}>
            {busy ? labels.submitting : labels.createUpload}
          </button>
        </div>

        <div className="path-box">
          <h3>{labels.pathIntake}</h3>
          <p>{labels.pathHelp}</p>
          <textarea
            value={pathText}
            onChange={(event) => setPathText(event.target.value)}
            placeholder={"C:\\Data\\contracts\\batch-a\nC:\\Exports\\mailbox\\thread.eml"}
          />
          <button
            disabled={busy || pathText.trim().length === 0}
            onClick={() =>
              onSubmitPaths(
                pathText
                  .split(/\r?\n/)
                  .map((line) => line.trim())
                  .filter(Boolean),
                tenantId
              )
            }
          >
            {busy ? labels.submitting : labels.createPath}
          </button>
        </div>
      </div>
    </section>
  );
}
