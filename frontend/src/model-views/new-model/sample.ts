import { hyperStyled } from "@macrostrat/hyper";
import { useState, useContext } from "react";
import MapGL from "@urbica/react-map-gl";
import Draw from "@urbica/react-map-gl-draw";
import { FormSlider } from "./utils";
import styles from "./module.styl";

const h = hyperStyled(styles);

function NewSampleMap(props) {
  const [point, setPoint] = useState({
    type: "Feature",
    properties: {},
    geometry: {
      coordinates: [0, 0],
      type: "Point",
    },
  });

  console.log(point);
  const handleChange = ({ features }) => {
    const { geometry } = features[0];
    setPoint((prevPoint) => {
      return {
        ...point,
        geometry,
      };
    });
    const { coordinates } = geometry;
    const [longitude, latitude] = coordinates;
  };

  return h(
    MapGL,
    {
      className: "map",
      style: { width: "100%", height: "400px" },
      mapStyle: "mapbox://styles/mapbox/light-v9",
      accessToken: process.env.MAPBOX_API_TOKEN,
      latitude: 37.78,
      longitude: -122.41,
      zoom: 0,
    },
    [
      h(Draw, {
        //data: point,
        onChange: handleChange,
        polygonControl: false,
        lineStringControl: false,
        uncombineFeaturesControl: false,
        combineFeaturesControl: false,
      }),
    ]
  );
}

/**
 * Things Needed on a Sample Form
 * depth
 * elevation
 * embargo_date
 * igsn
 * location: lat/lng
 * material
 * name
 * projects
 * sample_geo_entity => geo formations (macrostrat)
 * session_collection
 * data_file_links?
 *
 */
function NewSampleForm(props) {
  const [sample, setSample] = useState({
    name: "",
    depth: 0,
    elevation: 0,
    latitude: 0,
    longitude: 0,
    material: "",
    sample_geo_entity: "",
  });
  const { context } = props;

  return h(NewSampleMap);
}

function NewSampleToModel(props) {
  const { context } = props;

  return h("div", [
    h(FormSlider, {
      content: h(NewSampleForm),
      model: "sample",
    }),
  ]);
}

export { NewSampleToModel };
