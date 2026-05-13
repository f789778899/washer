import { DocumentDetail, DocumentSummary } from "../lib/api";

type DocumentPanelProps = {
  documents: DocumentSummary[];
  selectedDocumentId: string | null;
  documentDetail: DocumentDetail | null;
  onSelect: (documentId: string) => void;
  labels: {
    title: string;
    description: string;
    empty: string;
    noRedaction: string;
    quality: string;
    viewer: string;
    viewerHelp: string;
    noSelection: string;
    markdown: string;
    metadata: string;
    cleaning: string;
    dedup: string;
    sensitive: string;
  };
};

export function DocumentPanel({
  documents,
  selectedDocumentId,
  documentDetail,
  onSelect,
  labels
}: DocumentPanelProps) {
  return (
    <section className="document-layout">
      <div className="panel doc-list-panel">
        <div className="panel-header">
          <div>
            <h2>{labels.title}</h2>
            <p>{labels.description}</p>
          </div>
        </div>
        <div className="doc-list">
          {documents.length === 0 ? <div className="empty-state">{labels.empty}</div> : null}
          {documents.map((document) => (
            <button
              key={document.document_id}
              className={`doc-card ${selectedDocumentId === document.document_id ? "active" : ""}`}
              onClick={() => onSelect(document.document_id)}
            >
              <div className="doc-card-top">
                <strong>{document.filename}</strong>
                <span className={`status status-${document.dedup_status}`}>{document.dedup_status}</span>
              </div>
              <div className="doc-card-meta">
                <span>{document.doc_type}</span>
                <span>{document.language}</span>
                <span>{labels.quality} {document.quality_score}</span>
              </div>
              <div className="chip-row">
                {document.sensitive_fields.length === 0 ? (
                  <span className="chip muted">{labels.noRedaction}</span>
                ) : (
                  document.sensitive_fields.map((field) => (
                    <span key={field} className="chip">
                      {field}
                    </span>
                  ))
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="panel doc-detail-panel">
        <div className="panel-header">
          <div>
            <h2>{labels.viewer}</h2>
            <p>{labels.viewerHelp}</p>
          </div>
        </div>
        {!documentDetail ? (
          <div className="empty-state">{labels.noSelection}</div>
        ) : (
          <div className="detail-grid">
            <div>
              <h3>{labels.markdown}</h3>
              <pre className="code-view">{documentDetail.markdown_text}</pre>
            </div>
            <div>
              <h3>{labels.metadata}</h3>
              <pre className="code-view">{JSON.stringify(documentDetail.metadata, null, 2)}</pre>
            </div>
            <div>
              <h3>{labels.cleaning}</h3>
              <ul className="plain-list">
                {documentDetail.audit.cleaning_actions.map((item) => (
                  <li key={`${item.action}-${item.detail}`}>
                    {item.action}: {item.detail} ({item.count})
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3>{labels.dedup}</h3>
              <ul className="plain-list">
                {documentDetail.audit.dedup_relations.map((item, index) => (
                  <li key={`${item.relation_type}-${index}`}>
                    {item.relation_type}: {item.reason} ({item.similarity})
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3>{labels.sensitive}</h3>
              <ul className="plain-list">
                {documentDetail.audit.sensitive_matches.map((item, index) => (
                  <li key={`${item.rule_id}-${index}`}>
                    {item.field_type}: {item.placeholder} via {item.rule_id}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
