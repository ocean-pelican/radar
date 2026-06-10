import { useState } from "react";
import MapView from "./MapView";
import DetectionPanel from "./DetectionPanel";
import ImageUploader from "./ImageUploader";

export default function App() {
  const [geojson, setGeojson] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>

      {/* Top bar — image upload controls */}
      <ImageUploader
        onDetections={setGeojson}
        onLoading={setLoading}
        loading={loading}
      />

      {/* Main content — map + sidebar */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>

        {/* Map takes up all remaining space */}
        <div style={{ flex: 1 }}>
          <MapView geojson={geojson} />
        </div>

        {/* Detection panel on the right */}
        <DetectionPanel geojson={geojson} loading={loading} />

      </div>
    </div>
  );
}