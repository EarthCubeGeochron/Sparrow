import { useState, useEffect, useRef } from "react";
import h from "@macrostrat/hyper";
import MapGl from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { Editor, DrawRectangleMode, EditingMode } from "react-map-gl-draw";
import { Card, NumericInput } from "@blueprintjs/core";

interface coordinates {
  minlng: number;
  maxlng: number;
  minlat: number;
  maxlat: number;
}

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
    selectedFeature: null,
  });
  const [coordinates, setCoordinates] = useState<coordinates>({
    minlng: 0,
    maxlng: 0,
    minlat: 0,
    maxlat: 0,
  });

  const [test, setTest] = useState();
  console.log(test);

  console.log(state.selectedFeature);
  console.log(coordinates);
  const mapRef = useRef();
  const editorRef = useRef();

  const onUpdate = (object) => {
    setState({ ...state, selectedFeature: object.data });
    console.log(object);
    // const geometry = object.data.map((object) => object.geometry);
    // const coordinates = geometry.map((object) => object.coordinates);
  };

  const bounds = mapRef.current
    ? //@ts-ignore
      mapRef.current.getMap().getBounds().toArray().flat()
    : null;

  const ModeHandler = state.selectedFeature
    ? state.selectedFeature.length >= 1
      ? new EditingMode()
      : new DrawRectangleMode()
    : new DrawRectangleMode();

  useEffect(() => {
    if (state.selectedFeature != null) {
      const geometry = state.selectedFeature.map((object) => object.geometry);
      const coordinates = geometry.map((object) => object.coordinates);
      //console.log(coordinates);
      coordinates.forEach((array) =>
        array.forEach((element) => {
          setCoordinates({
            minlng: element[0][0],
            minlat: element[1][1],
            maxlng: element[2][0],
            maxlat: element[0][1],
          });
        })
      );
    }
  }, [state.selectedFeature]);

  const setFeature = (GEOJsonObject) => {
    //setState({ ...state, selectedFeature: GEOJsonObject });
    setTest(GEOJsonObject);
  };

  return h("div", { style: { display: "flex" } }, [
    h(MapFilterInputs, { coordinates: coordinates, setFeature: setFeature }),
    h(Card, [
      h(
        MapGl,
        {
          mapStyle: state.MapStyle,
          mapboxApiAccessToken: process.env.MAPBOX_API_TOKEN,
          ...state.viewport,
          onViewportChange: (viewport) => {
            setState({
              ...state,
              //@ts-ignore
              viewport: viewport,
            });
          },
          ref: mapRef,
        },
        [
          h(Editor, {
            ref: editorRef,
            features: state.selectedFeature,
            //onSelect: console.log,
            onUpdate: onUpdate,
            mode: ModeHandler,
            clickRadius: 12,
          }),
        ]
      ),
    ]),
  ]);
}

export function MapFilterInputs({ coordinates, setFeature }) {
  const [state, setState] = useState<coordinates>({
    minlng: null,
    maxlng: null,
    minlat: null,
    maxlat: null,
  });
  console.log(state);

  useEffect(() => {
    setState(coordinates);
  }, [coordinates]);

  useEffect(() => {
    if (state != coordinates) {
      const featureList = [];
      const { maxlng, minlng, maxlat, minlat } = state;
      const feature = CoordinatesToGEOJson({ maxlng, minlng, maxlat, minlat });
      featureList.push(feature);
      console.log(featureList);

      setFeature(featureList);
    }
  }, [state]);

  return h(Card, [
    h("div", [
      h("p"),
      ["Maximum Longitude:"],
      h("br"),
      h(NumericInput, {
        defaultValue: state.maxlng,
        value: Number(state.maxlng).toFixed(0),
        onValueChange: (change) => setState({ ...state, maxlng: change }),
        min: -180,
        max: 180,
      }),
    ]),
    h("div", [
      h("p"),
      ["Minimum Longitude:"],
      h("br"),
      h(NumericInput, {
        defaultValue: state.minlng,
        value: Number(state.minlng).toFixed(0),
        onValueChange: (change) => setState({ ...state, minlng: change }),
        min: -180,
        max: 180,
      }),
    ]),
    h("div", [
      h("p"),
      ["Maximum Latitude:  "],
      h("br"),
      h(NumericInput, {
        defaultValue: state.maxlat,
        value: Number(state.maxlat).toFixed(0),
        onValueChange: (change) => setState({ ...state, maxlat: change }),
        min: -90,
        max: 90,
      }),
    ]),
    h("div", [
      h("p"),
      ["Minimum Latitude:  "],
      h("br"),
      h(NumericInput, {
        //defaultValue: minlat,
        value: Number(state.minlat).toFixed(0),
        onValueChange: (change) => setState({ ...state, minlat: change }),
        min: -90,
        max: 90,
      }),
    ]),
  ]);
}

export function CoordinatesToGEOJson({
  maxlng,
  minlng,
  maxlat,
  minlat,
}: coordinates) {
  return {
    type: "Feature",
    properties: {
      shape: "Rectangle",
    },
    geometry: {
      type: "Polygon",
      coordinates: [
        [
          [minlng, maxlat],
          [minlng, minlat],
          [maxlng, minlat],
          [maxlng, maxlat],
          [minlng, maxlat],
        ],
      ],
    },
  };
}
