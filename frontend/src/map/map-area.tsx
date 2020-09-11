/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import * as React from "react";
import { useState, useEffect, useRef } from "react";
import MapGl, { Marker, FlyToInterpolator } from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { mapStyles } from "../../plugins/MapStyle";
import h, { compose } from "@macrostrat/hyper";
import useSuperCluster from "use-supercluster";
import { Button, Intent, Toaster, Position } from "@blueprintjs/core";
import classNames from "classnames";
import "./cluster.css";
import { Link } from "react-router-dom";
import { useAPIResult, useToggle } from "./components/APIResult";
import { LayerMenu } from "./components/LayerMenu";
import { MarkerCluster } from "./components/MarkerCluster";
import { FilterMenu } from "./components/filterMenu";
import { MapToast } from "./components/MapToast";

const MapToaster = Toaster.create({
  position: Position.TOP_RIGHT,
  maxToasts: 1,
});

interface MapProps {
  on_map?: boolean;
  hide_filter?: boolean;
  width?: any;
  height?: any;
  latitude?: number;
  longitude?: number;
  zoom?: number;
  mapstyle?: any;
}

export function MapPanel({
  on_map,
  hide_filter = false,
  width = "50vw",
  height = "500px",
  latitude = 0,
  longitude = 0,
  zoom = 1,
  mapstyle = "mapbox://styles/mapbox/outdoors-v9",
}: MapProps) {
  const initialState = {
    viewport: { latitude, longitude, zoom, width, height },
    MapStyle: mapstyle,
    showMarkers: true,
    clickPnt: { lng: 0, lat: 0 },
  };

  const [state, setState] = useState(initialState);

  const mapRef = useRef();

  const bounds = mapRef.current
    ? mapRef.current
        .getMap()
        .getBounds()
        .toArray()
        .flat()
    : null;

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
      clickPnt: { lng: e.lngLat[0], lat: e.lngLat[1] },
    });
    if (hide_filter == false) {
      return MapToaster.show({
        message: (
          <MapToast
            mapstyle={state.MapStyle}
            lng={e.lngLat[0]}
            lat={e.lngLat[1]}
          />
        ),
        timeout: 0,
      });
    }
  };

  return (
    <div className="map-container">
      <div className="layer-button">
        <Link to="/">
          <Button icon="home"></Button>
        </Link>
        <LayerMenu
          hide={hide_filter}
          MapStyle={state.MapStyle}
          chooseMapStyle={chooseMapStyle}
          mapstyles={mapStyles}
          showMarkers={state.showMarkers}
          toggleShowMarkers={toggleShowMarkers}
        ></LayerMenu>
        <FilterMenu hide={hide_filter} on_map={on_map}></FilterMenu>
      </div>
      <div>
        <MapGl
          onClick={(e) => {
            mapClicked(e);
          }}
          mapStyle={state.MapStyle}
          mapboxApiAccessToken={process.env.MAPBOX_API_TOKEN}
          {...state.viewport}
          onViewportChange={(viewport) => {
            setState({ ...state, viewport: viewport });
          }}
          ref={mapRef}
        >
          {state.showMarkers ? (
            <MarkerCluster
              viewport={state.viewport}
              changeViewport={changeViewport}
              bounds={bounds}
            ></MarkerCluster>
          ) : null}
        </MapGl>
      </div>
    </div>
  );
}
