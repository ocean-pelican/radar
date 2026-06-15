import { useRef } from "react";

const API_BASE = "http://localhost:8000/api/v1";
const POLL_INTERVAL_MS = 1500;   // check every 1.5 seconds
const MAX_POLLS = 40;             // give up after 60 seconds

export default function ImageUploader({ onDetections, onLoading, loading, onStatus }) {
  const fileRef = useRef(null);

  async function pollForResult(jobId, attempts = 0) {
    if (attempts >= MAX_POLLS) {
      onLoading(false);
      onStatus("Job timed out — try again.");
      return;
    }

    const response = await fetch(`${API_BASE}/jobs/${jobId}`);
    const data = await response.json();

    if (data.status === "complete") {
      onDetections(data.result.geojson);
      onLoading(false);
      onStatus(`Complete — ${data.result.total_detections} detections`);

    } else if (data.status === "failed") {
      onLoading(false);
      onStatus(`Failed: ${data.error}`);

    } else {
      // Still queued or processing — poll again
      onStatus(data.status === "queued" ? "Queued..." : "Processing...");
      setTimeout(() => pollForResult(jobId, attempts + 1), POLL_INTERVAL_MS);
    }
  }

  async function handleSubmit() {
    const file = fileRef.current.files[0];
    if (!file) return;

    onLoading(true);
    onStatus("Submitting...");

    try {
      // Submit job
      const formData = new FormData();
      formData.append("file", file);

      const submitResponse = await fetch(`${API_BASE}/detect/async`, {
        method: "POST",
        body: formData
      });

      if (!submitResponse.ok) {
        throw new Error(`Submit failed: ${submitResponse.status}`);
      }

      const { job_id } = await submitResponse.json();
      onStatus("Queued...");

      // Start polling
      setTimeout(() => pollForResult(job_id), POLL_INTERVAL_MS);

    } catch (err) {
      console.error(err);
      onLoading(false);
      onStatus(`Error: ${err.message}`);
    }
  }

  return (
    <div style={{
      padding: "12px 16px",
      background: "#161b27",
      borderBottom: "1px solid #2d3748",
      display: "flex",
      alignItems: "center",
      gap: "12px",
    }}>
      <span style={{ fontSize: "13px", color: "#64748b", fontFamily: "monospace" }}>
        SENTINEL LITE //
      </span>
      <input
        ref={fileRef}
        type="file"
        accept=".jpg,.jpeg,.png"
        style={{ fontSize: "13px", color: "#e2e8f0", flex: 1 }}
      />
      <button
        onClick={handleSubmit}
        disabled={loading}
        style={{
          padding: "8px 20px",
          background: loading ? "#2d3748" : "#3b82f6",
          color: "white",
          border: "none",
          borderRadius: "6px",
          cursor: loading ? "not-allowed" : "pointer",
          fontSize: "13px",
          fontWeight: "bold",
        }}
      >
        {loading ? "Processing..." : "Detect"}
      </button>
    </div>
  );
}