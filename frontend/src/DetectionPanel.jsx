const CLASS_COLORS = {
  car: "#3b82f6",
  pedestrian: "#22c55e",
  people: "#16a34a",
  truck: "#a855f7",
  van: "#ef4444",
  bus: "#ec4899",
  bicycle: "#f97316",
  motor: "#6366f1",
  tricycle: "#06b6d4",
  "awning-tricycle": "#eab308",
};

export default function DetectionPanel({ geojson, loading }) {
  const detections = geojson ? geojson.features : [];

  // Count by class for the summary header
  const counts = detections.reduce((acc, f) => {
    const cls = f.properties.class_name;
    acc[cls] = (acc[cls] || 0) + 1;
    return acc;
  }, {});

  return (
    <div style={{
      width: "280px",
      height: "100%",
      background: "#161b27",
      borderLeft: "1px solid #2d3748",
      display: "flex",
      flexDirection: "column",
      overflow: "hidden",
    }}>

      {/* Header */}
      <div style={{ padding: "16px", borderBottom: "1px solid #2d3748" }}>
        <div style={{ fontSize: "11px", color: "#64748b", letterSpacing: "0.1em" }}>
          SENTINEL LITE
        </div>
        <div style={{ fontSize: "18px", fontWeight: "bold", marginTop: "2px" }}>
          Detections
        </div>
        {detections.length > 0 && (
          <div style={{ fontSize: "13px", color: "#64748b", marginTop: "4px" }}>
            {detections.length} total
          </div>
        )}
      </div>

      {/* Class summary */}
      {Object.keys(counts).length > 0 && (
        <div style={{ padding: "12px 16px", borderBottom: "1px solid #2d3748" }}>
          {Object.entries(counts).map(([cls, count]) => (
            <div key={cls} style={{
              display: "flex",
              justifyContent: "space-between",
              padding: "3px 0",
              fontSize: "13px"
            }}>
              <span style={{ color: CLASS_COLORS[cls] || "#94a3b8" }}>
                {cls}
              </span>
              <span style={{ color: "#94a3b8" }}>{count}</span>
            </div>
          ))}
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div style={{ padding: "24px", textAlign: "center", color: "#64748b" }}>
          Running detection...
        </div>
      )}

      {/* Empty state */}
      {!loading && detections.length === 0 && (
        <div style={{ padding: "24px", textAlign: "center", color: "#64748b", fontSize: "13px" }}>
          Upload a drone image to begin.
        </div>
      )}

      {/* Detection list */}
      <div style={{ flex: 1, overflowY: "auto" }}>
        {detections.map((f, i) => {
          const { class_name, confidence } = f.properties;
          const [lon, lat] = f.geometry.coordinates;
          return (
            <div key={i} style={{
              padding: "10px 16px",
              borderBottom: "1px solid #1e2433",
              fontSize: "12px",
            }}>
              <div style={{
                color: CLASS_COLORS[class_name] || "#94a3b8",
                fontWeight: "bold",
                marginBottom: "2px"
              }}>
                {class_name.toUpperCase()}
              </div>
              <div style={{ color: "#64748b" }}>
                {(confidence * 100).toFixed(1)}% confidence
              </div>
              <div style={{ color: "#475569", fontFamily: "monospace", fontSize: "11px" }}>
                {lat.toFixed(5)}, {lon.toFixed(5)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}