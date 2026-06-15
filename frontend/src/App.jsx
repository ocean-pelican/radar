import { useState } from "react";
import MapView from "./MapView";
import DetectionPanel from "./DetectionPanel";
import ImageUploader from "./ImageUploader";

export default function App() {
  const [geojson, setGeojson] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("Upload a drone image to begin.");

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>

      <ImageUploader
        onDetections={setGeojson}
        onLoading={setLoading}
        loading={loading}
        onStatus={setStatus}
      />

      {/* Status bar */}
      <div style={{
        padding: "6px 16px",
        background: "#0f1117",
        borderBottom: "1px solid #2d3748",
        fontSize: "12px",
        color: "#64748b",
        fontFamily: "monospace"
      }}>
        {status}
      </div>

      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <div style={{ flex: 1 }}>
          <MapView geojson={geojson} />
        </div>
        <DetectionPanel geojson={geojson} loading={loading} />
      </div>

    </div>
  );
}