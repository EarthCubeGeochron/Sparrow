import * as React from "react";
import { useState, useEffect, useRef } from "react";
import h from "@macrostrat/hyper";
import MapGl, { Marker } from "react-map-gl";
import { Card, Icon, Button, Popover } from "@blueprintjs/core";
import { MyNumericInput } from "../../new-sample/edit-sample";

/**
 * This can be used to set Latitude and Longitude fields in datasheet or other components.
 * Click on the map to drop a marker and fill info
 * Dragging Marker would be good too
 */

export function MapSelector({ width = "50vw", height = "500px", zoom = 0 }) {
  const [state, setState] = useState({
    MapStyle: "mapbox://styles/mapbox/outdoors-v9",
    viewport: {
      width: width,
      height: height,
      latitude: 30,
      longitude: 0,
      zoom: zoom,
    },
    longitude: null,
    latitude: null,
  });

  console.log(state.latitude, state.longitude);

  const mapRef = useRef();

  const bounds = mapRef.current
    ? //@ts-ignore
      mapRef.current
        .getMap()
        .getBounds()
        .toArray()
        .flat()
    : null;

  const mapClicked = (e) => {
    setState({
      ...state,
      longitude: e.lngLat[0],
      latitude: e.lngLat[1],
    });
    const onDragEnd = (event) => {
      const [lng, lat] = event.lngLat;
      setState({ ...state, longitude: lng, latitude: lat });
    };
    function LongLatInputs() {
      const onChangeLng = (event) => {
        setState({ ...state, longitude: event.target.value });
      };
      const onChangeLat = (event) => {
        setState({ ...state, latitude: event.target.value });
      };
      return (
        h(MyNumericInput, {
          value: state.longitude,
          onChange: onChangeLng,
          helperText: "-180 to 180",
          label: "Longitude",
        }),
        h(MyNumericInput, {
          value: state.latitude,
          onChange: onChangeLat,
          helperText: "-90 to 90",
          label: "Latitude",
        })
      );
    }

    return h("div", { style: { display: "flex" } }, [
      h(Card, [
        h(
          MapGl,
          {
            onClick: (e) => mapClicked(e),
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
            h.if(state.longitude != null)(
              Marker,
              {
                longitude: state.longitude,
                latitude: state.latitude,
                draggable: true,
                onDragEnd,
              },
              [h(Icon, { icon: "map-marker" })]
            ),
          ]
        ),
        h(LongLatInputs),
      ]),
    ]);
  };
}
