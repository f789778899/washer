import { JobSummary } from "../lib/api";

type JobsPanelProps = {
  jobs: JobSummary[];
  selectedJobId: string | null;
  onSelect: (jobId: string) => void;
  labels: {
    title: string;
    description: string;
    id: string;
    status: string;
    tenant: string;
    sources: string;
    processed: string;
    failed: string;
    updated: string;
  };
};

export function JobsPanel({ jobs, selectedJobId, onSelect, labels }: JobsPanelProps) {
  return (
    <section className="panel jobs-panel">
      <div className="panel-header">
        <div>
          <h2>{labels.title}</h2>
          <p>{labels.description}</p>
        </div>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>{labels.id}</th>
              <th>{labels.status}</th>
              <th>{labels.tenant}</th>
              <th>{labels.sources}</th>
              <th>{labels.processed}</th>
              <th>{labels.failed}</th>
              <th>{labels.updated}</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr
                key={job.job_id}
                className={selectedJobId === job.job_id ? "selected" : ""}
                onClick={() => onSelect(job.job_id)}
              >
                <td>{job.job_id}</td>
                <td>
                  <span className={`status status-${job.status}`}>{job.status}</span>
                </td>
                <td>{job.tenant_id}</td>
                <td>{job.source_count}</td>
                <td>{job.processed_count}</td>
                <td>{job.failed_count}</td>
                <td>{new Date(job.updated_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
