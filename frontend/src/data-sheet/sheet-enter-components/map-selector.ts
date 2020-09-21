import * as React from "react";
import { useState, useEffect, useRef } from "react";
import h from "@macrostrat/hyper";
import MapGl, { Marker } from "react-map-gl";
import {
  Card,
  Icon,
  Button,
  Popover,
  Overlay,
  Dialog,
} from "@blueprintjs/core";
import { MyNumericInput } from "../../new-sample/edit-sample";
import {
  SaveButton,
  CancelButton,
  DeleteButton,
} from "@macrostrat/ui-components";
import { useToggle } from "../../map/components/APIResult";

/**
 * This can be used to set Latitude and Longitude fields in datasheet or other components.
 * Click on the map to drop a marker and fill info
 * Dragging Marker would be good too
 */

export function MapSelector({ onCellsChanged, row, col, colTwo }) {
  const [state, setState] = useState({
    viewport: {
      width: "100%",
      height: "500px",
      latitude: 30,
      longitude: 0,
      zoom: 0,
    },
    longitude: 0,
    latitude: 0,
  });

  const [open, toggle] = useToggle(true);

  const onClickHandle = () => {
    //col is latitude, colTwo is longitude if col < colTwo
    // col is longitude, colTwo is latitude of col > colTwo
    if (col > colTwo) {
      const latitude = Number(state.latitude).toFixed(3);
      const longitude = Number(state.longitude).toFixed(3);
      const changes = [
        { row: row, col: col, value: latitude },
        { row: row, col: colTwo, value: longitude },
      ];
      console.log(changes);
      onCellsChanged(changes);
      toggle;
    } else if (col > colTwo) {
      const latitude = Number(state.latitude).toFixed(3);
      const longitude = Number(state.longitude).toFixed(3);
      const changes = [
        { row: row, col: col, value: longitude },
        { row: row, col: colTwo, value: latitude },
      ];
      console.log(changes);
      onCellsChanged(changes);
      toggle;
    }
  };

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
  };
  const onDragEnd = (event) => {
    const [lng, lat] = event.lngLat;
    setState({ ...state, longitude: lng, latitude: lat });
  };
  function LongLatInputs() {
    const onChangeLng = (value) => {
      setState({ ...state, longitude: value });
    };
    const onChangeLat = (value) => {
      setState({ ...state, latitude: value });
    };
    return h(
      "div",
      { style: { display: "flex", justifyContent: "space-between" } },
      [
        h(MyNumericInput, {
          value: Number(state.longitude).toFixed(3),
          onChange: onChangeLng,
          helperText: "(-180 to 180)",
          min: -180,
          max: 180,
          label: "Longitude",
        }),
        h(MyNumericInput, {
          value: Number(state.latitude).toFixed(3),
          onChange: onChangeLat,
          helperText: "(-90 to 90)",
          label: "Latitude",
          min: -90,
          max: 90,
        }),
      ]
    );
  }

  return h("div", { style: { display: "flex" } }, [
    h(Dialog, { isOpen: open }, [
      h(Card, [
        h(
          MapGl,
          {
            onClick: (e) => mapClicked(e),
            mapStyle: "mapbox://styles/mapbox/outdoors-v9",
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
                offsetLeft: -10,
                offsetTop: -15,
              },
              [h(Icon, { icon: "map-marker" })]
            ),
          ]
        ),
        h(LongLatInputs),
        h("div", { style: { display: "flex", justifyContent: "flex-end" } }, [
          h(SaveButton, { onClick: onClickHandle }, ["Save Changes"]),
          h(CancelButton, { onClick: toggle }, ["Cancel"]),
        ]),
      ]),
    ]),
  ]);
}
