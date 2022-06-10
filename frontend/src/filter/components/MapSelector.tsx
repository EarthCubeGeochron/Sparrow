import { useState } from "react";
import h from "@macrostrat/hyper";
import MapGL from "@urbica/react-map-gl";
import Draw from "@urbica/react-map-gl-draw";
import { Card } from "@blueprintjs/core";
import { HelpButton } from "~/components";
import "mapbox-gl/dist/mapbox-gl.css";
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import { FilterAccordian } from "./utils";

/**
 * This component is meant to be a location filter for data.
 * The end goal would be to make a polygon or box and it would filter
 * data down to those only in that area
 * */

export function MapPolygon(props) {
  const { dispatch } = props;

  const [features, setFeatures] = useState({
    type: "Feature",
    properties: {},
    geometry: {
      coordinates: [
        [
          [0, 0],
          [0, 0],
          [0, 0],
          [0, 0],
          [0, 0],
        ],
      ],
      type: "Polygon",
    },
  });

  const handleChange = ({ features }) => {
    setFeatures(features[0]);
    const polygon = toWKT(features[0].geometry.coordinates[0]);
    dispatch({ type: "set-geometry", geometry: polygon });
  };

  const content = h("div", { style: { position: "relative" } }, [
    h(
      MapGL,
      {
        style: { width: "100%", height: "400px" },
        mapStyle: "mapbox://styles/mapbox/light-v9",
        accessToken: process.env.MAPBOX_API_TOKEN,
        latitude: 37.78,
        longitude: -122.41,
        zoom: 0,
      },
      [
        h(Draw, {
          onChange: handleChange,
          pointControl: false,
          lineStringControl: false,
          uncombineFeaturesControl: false,
          combineFeaturesControl: false,
        }),
      ]
    ),
    h("div", { style: { position: "absolute", top: "0" } }, [h(MapHelpButton)]),
  ]);

  return h(Card, [
    h(FilterAccordian, { content, text: "Select a Location on the map" }),
  ]);
}

/**
 * @description: function to create a WKT polygon from an array of points. Will use it for the map filter
 * @param {*} props
 * POLYGON((0 0,180 90,180 0,0 90,0 0))
 */
function toWKT(coords) {
  // create strings you can add together.
  let text_coords = "";
  for (let x of coords) {
    // x[0] x[1]
    const Lat = x[0].toFixed(3);
    const Long = x[1].toFixed(3);
    text_coords += `${Lat} ${Long},`;
  }
  text_coords = text_coords.slice(0, -1);
  return `POLYGON((${text_coords}))`;
}

/**
 * component that has some help info for basic
 * @param props
 */
function MapHelpButton(props) {
  const content = h("div", [
    h(Card, [
      h("p", ["Zoom in: Double Click"]),
      h("p", [
        "Zoom-Out: ",
        "Mac(Command+Shift+Doulbe Click), PC (Control+Shift+Double Click)",
      ]),
      h("p", ["Exit Drawing: Enter"]),
      h("p", ["Edit Existing Shape: Double Click Shape"]),
    ]),
  ]);

  return h(HelpButton, { content });
}
