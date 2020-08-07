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
  const [viewport, setViewport] = useState({
    latitude,
    longitude,
    zoom,
    width,
    height,
  });
  const [MapStyle, setMapStyle] = useState(mapstyle);
  const [showMarkers, setShowMarkers] = useState(true);
  const [clickPnt, setClickPnt] = useState({ lng: 0, lat: 0 });
  const [drawOpen, setDrawOpen] = useState(false);

  const mapstyles = {
    initialMapStyle: "mapbox://styles/mapbox/outdoors-v9",
    topoMapStyle: "mapbox://styles/jczaplewski/cjftzyqhh8o5l2rqu4k68soub",
    sateliteMapStyle: "mapbox://styles/jczaplewski/cjeycrpxy1yv22rqju6tdl9xb",
    mapStyle: mapStyle,
  };

  const mapRef = useRef();

  const initialData = useAPIResult("/sample", { all: true });

  const MacURl = "https://macrostrat.org/api/v2/geologic_units/map";

  const MacostratData = useAPIResult(MacURl, {
    lng: clickPnt.lng,
    lat: clickPnt.lat,
  });

  useEffect(() => {
    if (MacostratData == null) return;
    console.log(MacostratData.success.data);
  }, [MacostratData]);

  const bounds = mapRef.current
    ? mapRef.current.getMap().getBounds().toArray().flat()
    : null;

  return (
    <div className="map-container">
      <MapDrawer drawOpen={drawOpen} setDrawOpen={setDrawOpen}></MapDrawer>
      <div className="layer-button">
        <LayerMenu
          MapStyle={MapStyle}
          setMapStyle={setMapStyle}
          mapstyles={mapstyles}
          showMarkers={showMarkers}
          setShowMarkers={setShowMarkers}
        ></LayerMenu>
      </div>
      <div>
        <MapGl
          onClick={(e) => {
            setClickPnt({ lng: e.lngLat[0], lat: e.lngLat[1] });
            setDrawOpen(!drawOpen);
          }}
          mapStyle={MapStyle}
          mapboxApiAccessToken={process.env.MAPBOX_API_TOKEN}
          {...viewport}
          onViewportChange={(viewport) => {
            setViewport(viewport);
          }}
          ref={mapRef}
        >
          {showMarkers ? (
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
