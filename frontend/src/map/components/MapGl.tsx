import * as React from "react";
import { useState, useEffect, useRef } from "react";
import h from "@macrostrat/hyper";
import MapGl, { Marker, FlyToInterpolator } from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import {
  Editor,
  DrawRectangleMode,
  EditingMode,
  RENDER_STATE,
} from "react-map-gl-draw";
import { Card, InputGroup, NumericInput } from "@blueprintjs/core";

export function Map({ width = "50vw", height = "500px", zoom = 0 }) {
  const [state, setState] = useState({
    MapStyle: "mapbox://styles/mapbox/outdoors-v9",
    viewport: {
      width: width,
      height: height,
      latitude: 30,
      longitude: 0,
      zoom: zoom,
    },
    selectedFeature: {},
  });
  const [coordinates, setCoordinates] = useState({
    minlng: 0,
    maxlng: 0,
    minlat: 0,
    maxlat: 0,
  });
  const mapRef = useRef();
  const editorRef = useRef();

  const bounds = mapRef.current
    ? mapRef.current.getMap().getBounds().toArray().flat()
    : null;

  const featureList = [];
  console.log(state.selectedFeature);
  console.log(editorRef.current);
  return h("div", { style: { display: "flex" } }, [
    h(MapFilterInputs, { coordinates: coordinates }),
    h(Card, [
      h(
        MapGl,
        {
          mapStyle: state.MapStyle,
          mapboxApiAccessToken: process.env.MAPBOX_API_TOKEN,
          ...state.viewport,
          onViewportChange: (viewport) => {
            setState({ ...state, viewport: viewport });
          },
          ref: mapRef,
        },
        [
          h(Editor, {
            ref: editorRef,
            onSelect: (selected) => {
              setState({
                ...state,
                selectedFeature: selected.selectedFeature, // This returns an object with the geoJSON corresponding to the rectangle
              });
            },
            mode: new DrawRectangleMode(),
            clickRadius: 12,
          }),
        ]
      ),
    ]),
  ]);
}

export function MapFilterInputs({ coordinates }) {
  const { maxlng, minlng, maxlat, minlat } = coordinates;
  return h(Card, [
    h("div", [
      h("p"),
      ["Maximum Longitude:"],
      h("br"),
      h(NumericInput, { defaultValue: coordinates.maxlng }),
    ]),
    h("div", [
      h("p"),
      ["Minimum Longitude:"],
      h("br"),
      h(NumericInput, { defaultValue: coordinates.minlng }),
    ]),
    h("div", [
      h("p"),
      ["Maximum Latitude:  "],
      h("br"),
      h(NumericInput, { defaultValue: coordinates.maxlat }),
    ]),
    h("div", [
      h("p"),
      ["Minimum Latitude:  "],
      h("br"),
      h(NumericInput, { defaultValue: coordinates.minlat }),
    ]),
  ]);
}
