import React from "react";
import h from "@macrostrat/hyper";
import {
  ComposableMap,
  ZoomableGlobe,
  Geographies,
  Geography,
  Marker,
  Markers,
} from "react-simple-maps";
import worldMap from "./assets/land-110m.json";
import { useAPIv2Result } from "~/api-v2";
import { Colors } from "@blueprintjs/core";
import { useHistory } from "react-router-dom";

function MapComponent(props) {
  let { markers } = props;
  const history = useHistory();

  if (markers == null) {
    markers = [];
  }
  const style = {
    fill: "#e9fcea",
    stroke: Colors.GRAY5,
    strokeWidth: 0.75,
    outline: "none",
  };

  return (
    <div>
      <ComposableMap
        projection="orthographic"
        projectionConfig={{
          scale: 400,
        }}
        width={820}
        height={820}
        style={{
          width: "100%",
          height: "auto",
          maxHeight: "500px",
        }}
      >
        <ZoomableGlobe
          center={[-120, 35]}
          fill="#afe6f0"
          stroke="#eceff1"
          //style={{ cursor: "move" }}
        >
          <circle cx={410} cy={410} r={400} fill="#afe6f0" stroke="#888888" />
          <Geographies geography={worldMap} disableOptimization>
            {(geographies, projection) => {
              console.log(projection);
              return geographies.map((geography, i) => {
                return (
                  <Geography
                    key={i}
                    geography={geography}
                    projection={projection}
                    style={{
                      default: style,
                      hover: style,
                      pressed: style,
                    }}
                  />
                );
              });
            }}
          </Geographies>
          <Markers>
            {markers.map((marker, i) => {
              return (
                <Marker
                  key={i}
                  marker={marker}
                  style={{
                    default: { fill: "#ad99ff" },
                    hover: { fill: "#634dbf" },
                    pressed: { fill: "#FF5722" },
                    hidden: { opacity: 0 },
                    cursor: "pointer",
                  }}
                >
                  <circle
                    cx={0}
                    cy={0}
                    r={10}
                    style={{
                      stroke: "#634dbf",
                      strokeWidth: 3,
                      opacity: 0.9,
                    }}
                    onClick={function () {
                      history.push(`/catalog/sample/${marker.id}`);
                    }}
                  />
                </Marker>
              );
            })}
          </Markers>
        </ZoomableGlobe>
      </ComposableMap>
    </div>
  );
}

function getMarkers() {
  const data = useAPIv2Result(
    "/map-samples",
    {},
    {
      unwrapResponse: (data) => {
        const markers = data.data.map((d) => {
          const { id, name, location } = d;
          const { coordinates } = location;
          return { id, name, coordinates };
        });
        return markers;
      },
    }
  );
  if (!data) {
    return [];
  }
  return data;
}

function SampleMap() {
  let markers = getMarkers();

  return h("div", [
    h(
      "h4",
      `${markers.length} measurements have been linked to their geologic metadata`
    ),
    h(MapComponent, { markers }),
  ]);
}

export { MapComponent, SampleMap };
