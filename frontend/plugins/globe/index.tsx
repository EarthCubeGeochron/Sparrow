/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import React, { Component } from "react";
import h from "react-hyperscript";
import {
  ComposableMap,
  ZoomableGlobe,
  Geographies,
  Geography,
  Graticule,
  Markers,
} from "react-simple-maps";
import worldMap from "./assets/land-110m.json";
import { APIResultView } from "@macrostrat/ui-components";
import { Colors, H1, Tooltip } from "@blueprintjs/core";
import {Marker} from 'react-map-gl';
//import { Tooltip } from "@material-ui/core";

class MapComponent extends Component {
  render() {
    let { markers } = this.props;
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
            style={{ cursor: "move" }}
          >
            <circle cx={410} cy={410} r={400} fill="#afe6f0" stroke="#888888" />
            <Geographies geography={worldMap} disableOptimization>
              {(geographies, projection) => {
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
}

class SampleMap extends Component {
  render() {
    const route = "/sample";
    const params = { geometry: "%", all: true };
    return h(APIResultView, { route, params }, (data) => {
      const markers = data
        .filter((d) => d.geometry != null)
        .map((d) => ({
          coordinates: d.geometry.coordinates,
          name: d.id,
        }));

      return h("div", [
        h(
          "h4",
          `${markers.length} measurements have been linked to their geologic metadata`
        ),
        h(MapComponent, { markers }),
      ]);
    });
  }
}

export { MapComponent, SampleMap };
