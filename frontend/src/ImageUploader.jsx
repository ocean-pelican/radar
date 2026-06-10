import { useRef } from "react";

export default function ImageUploader({ onDetections, onLoading, loading }) {
  const fileRef = useRef(null);

  async function handleSubmit(e) {
    e.preventDefault();
    const file = fileRef.current.files[0];
    if (!file) return;

    onLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        "http://localhost:8000/api/v1/detect/geojson",
        { method: "POST", body: formData }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const geojson = await response.json();
      onDetections(geojson);

    } catch (err) {
      console.error("Detection failed:", err);
      alert(`Detection failed: ${err.message}`);
    } finally {
      onLoading(false);
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
          transition: "background 0.2s",
        }}
      >
        {loading ? "Processing..." : "Detect"}
      </button>
    </div>
  );
}