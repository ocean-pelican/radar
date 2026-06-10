import { Marker, Popup } from "react-leaflet";
import L from "leaflet";

// Color per class — matches the colors from your Python inference script
const CLASS_COLORS = {
  car:             "#3b82f6",   // blue
  pedestrian:      "#22c55e",   // green
  people:          "#16a34a",   // dark green
  truck:           "#a855f7",   // purple
  van:             "#ef4444",   // red
  bus:             "#ec4899",   // pink
  bicycle:         "#f97316",   // orange
  motor:           "#6366f1",   // indigo
  tricycle:        "#06b6d4",   // cyan
  "awning-tricycle": "#eab308", // yellow
};

const DEFAULT_COLOR = "#94a3b8"; // slate for unknowns

// Build a colored circle marker for each detection class
function makeIcon(className) {
  const color = CLASS_COLORS[className] || DEFAULT_COLOR;
  return L.divIcon({
    className: "",
    html: `
      <div style="
        width: 12px;
        height: 12px;
        background: ${color};
        border: 2px solid white;
        border-radius: 50%;
        box-shadow: 0 0 4px rgba(0,0,0,0.5);
      "></div>
    `,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  });
}

export default function DetectionMarker({ feature }) {
  const { coordinates } = feature.geometry;
  const { class_name, confidence, timestamp } = feature.properties;

  // GeoJSON is [longitude, latitude] — Leaflet wants [latitude, longitude]
  const position = [coordinates[1], coordinates[0]];

  return (
    <Marker position={position} icon={makeIcon(class_name)}>
      <Popup>
        <div style={{ fontFamily: "monospace", fontSize: "13px", minWidth: "160px" }}>
          <div style={{ fontWeight: "bold", marginBottom: "4px", color: CLASS_COLORS[class_name] || DEFAULT_COLOR }}>
            {class_name.toUpperCase()}
          </div>
          <div>Confidence: {(confidence * 100).toFixed(1)}%</div>
          <div>Lat: {coordinates[1].toFixed(6)}</div>
          <div>Lon: {coordinates[0].toFixed(6)}</div>
          {timestamp && (
            <div style={{ marginTop: "4px", color: "#94a3b8", fontSize: "11px" }}>
              {new Date(timestamp).toLocaleTimeString()}
            </div>
          )}
        </div>
      </Popup>
    </Marker>
  );
}