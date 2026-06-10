import { MapContainer, TileLayer, useMap } from "react-leaflet";
import DetectionMarker from "./DetectionMarker";
import { useEffect } from "react";

// Default center — McKinney TX, where your TEST_PARAMS point
const DEFAULT_CENTER = [33.1972, -96.6397];
const DEFAULT_ZOOM = 15;

// This child component handles auto-fitting the map bounds
// when new detections arrive so you don't have to manually pan
function FitBounds({ geojson }) {
  const map = useMap();

  useEffect(() => {
    if (!geojson || geojson.features.length === 0) return;

    const coords = geojson.features.map((f) => [
      f.geometry.coordinates[1],
      f.geometry.coordinates[0],
    ]);

    if (coords.length === 1) {
      map.setView(coords[0], 17);
    } else {
      map.fitBounds(coords, { padding: [40, 40] });
    }
  }, [geojson, map]);

  return null;
}

export default function MapView({ geojson }) {
  return (
    <MapContainer
      center={DEFAULT_CENTER}
      zoom={DEFAULT_ZOOM}
      style={{ height: "100%", width: "100%", background: "#1e2433" }}
    >
      {/* OpenStreetMap tile layer — free, no API key required */}
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />

      {/* Auto-fit map when detections arrive */}
      {geojson && <FitBounds geojson={geojson} />}

      {/* Render one marker per detection */}
      {geojson &&
        geojson.features.map((feature, i) => (
          <DetectionMarker key={i} feature={feature} />
        ))}
    </MapContainer>
  );
}