/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import React, { useState, useEffect, useRef, useContext } from "react";
import MapGl, { Marker, FlyToInterpolator } from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { mapStyle } from "./MapStyle";
import h, { compose } from "@macrostrat/hyper";
import useSuperCluster from "use-supercluster";
import { Tooltip, Popover, Button, Intent } from "@blueprintjs/core";
import classNames from "classnames";
import "./cluster.css";
import { Link } from "react-router-dom";
import { useAPIResult } from "./components/APIResult";
import { LayerMenu } from "./components/LayerMenu";
import { MarkerCluster } from "./components/MarkerCluster";
import { MapDrawer } from "./components/MapDrawer";

export function MapPanel({
  width = "50vw",
  height = "500px",
  latitude = 0,
  longitude = 0,
  zoom = 1,
  mapstyle = "mapbox://styles/mapbox/outdoors-v9",
}) {
  const initialState = {
    viewport: { latitude, longitude, zoom, width, height },
    MapStyle: mapstyle,
    showMarkers: true,
    clickPnt: { lng: 0, lat: 0 },
    drawOpen: false,
  };

  const [state, setState] = useState(initialState);

  const [viewport, setViewport] = useState({
    latitude,
    longitude,
    zoom,
    width,
    height,
  });
  const mapstyles = {
    initialMapStyle: "mapbox://styles/mapbox/outdoors-v9",
    topoMapStyle: "mapbox://styles/jczaplewski/cjftzyqhh8o5l2rqu4k68soub",
    sateliteMapStyle: "mapbox://styles/jczaplewski/cjeycrpxy1yv22rqju6tdl9xb",
    mapStyle: mapStyle,
  };

  const mapRef = useRef();

  const bounds = mapRef.current
    ? mapRef.current.getMap().getBounds().toArray().flat()
    : null;

  const closeToast = () => {
    setState({ ...state, drawOpen: !state.drawOpen });
  };

  const toggleShowMarkers = () => {
    setState({ ...state, showMarkers: !state.showMarkers });
  };

  const chooseMapStyle = (props) => {
    setState({ ...state, MapStyle: props });
  };

  const changeViewport = ({ expansionZoom, longitude, latitude }) => {
    setState({
      ...state,
      viewport: {
        ...state.viewport,
        longitude: longitude,
        latitude: latitude,
        zoom: expansionZoom,
        transitionInterpolator: new FlyToInterpolator({
          speed: 1,
        }),
        transitionDuration: "auto",
      },
    });
  };

  const mapClicked = (e) => {
    setState({
      ...state,
      drawOpen: !state.drawOpen,
      clickPnt: { lng: e.lngLat[0], lat: e.lngLat[1] },
    });
  };

  return (
    <div className="map-container">
      <MapDrawer
        drawOpen={state.drawOpen}
        closeToast={closeToast}
        clickPnt={state.clickPnt}
      ></MapDrawer>
      <div className="layer-button">
        <LayerMenu
          MapStyle={state.MapStyle}
          chooseMapStyle={chooseMapStyle}
          mapstyles={mapstyles}
          showMarkers={state.showMarkers}
          toggleShowMarkers={toggleShowMarkers}
        ></LayerMenu>
      </div>
      <div>
        <MapGl
          onClick={(e) => {
            mapClicked(e);
          }}
          mapStyle={state.MapStyle}
          mapboxApiAccessToken={process.env.MAPBOX_API_TOKEN}
          {...viewport}
          onViewportChange={(viewport) => {
            setViewport(viewport);
          }}
          ref={mapRef}
        >
          {state.showMarkers ? (
            <MarkerCluster
              viewport={viewport}
              setViewport={setViewport}
              bounds={bounds}
            ></MarkerCluster>
          ) : null}
        </MapGl>
      </div>
    </div>
  );
}
