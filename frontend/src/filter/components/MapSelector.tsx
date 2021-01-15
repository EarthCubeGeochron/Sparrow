import React, { useState, useEffect } from "react";
import h from "@macrostrat/hyper";
import MapGL from "@urbica/react-map-gl";
import Draw from "@urbica/react-map-gl-draw";
import "mapbox-gl/dist/mapbox-gl.css";
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";

/**
 * This component is meant to be a location filter for data.
 * The end goal would be to make a polygon or box and it would filter
 * data down to those only in that area
 * */

export function MapPolygon(props) {
  const { updateParams } = props;

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
    console.log(features[0]);
    const polygon = toWKT(features[0].geometry.coordinates[0]);
    updateParams("geometry", polygon);
  };

  return h("div", [
    h(
      MapGL,
      {
        style: { width: "100%", height: "400px" },
        mapStyle: "mapbox://styles/mapbox/light-v9",
        accessToken:
          "pk.eyJ1IjoiamN6YXBsZXdza2kiLCJhIjoiWnQxSC01USJ9.oleZzfREJUKAK1TMeCD0bg",
        latitude: 37.78,
        longitude: -122.41,
        zoom: 1,
      },
      [
        h(Draw, {
          //data: features,
          onChange: handleChange,
        }),
      ]
    ),
    h("div", [JSON.stringify(toWKT(features.geometry.coordinates[0]))]),
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
    text_coords += `${x[0]} ${x[1]},`;
  }
  text_coords = text_coords.slice(0, -1);
  return `POLYGON((${text_coords}))`;
}
