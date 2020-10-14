import * as React from "react";
import { useState, useRef, useEffect } from "react";
import MapGl, { FlyToInterpolator, Marker } from "react-map-gl";
//import "mapbox-gl/dist/mapbox-gl.css";
import { mapStyles } from "../../plugins/MapStyle";
import { Toaster, Position, Icon, Navbar } from "@blueprintjs/core";
import "./cluster.css";
//import { Link } from "react-router-dom";
import { LayerMenu } from "./components/LayerMenu";
import { MarkerCluster } from "./components/MarkerCluster";
import { FilterMenu } from "./components/filterMenu";
import { MapToast } from "./components/MapToast";
import { useAPIResult, use } from "@macrostrat/ui-components";
import { MapNav } from "./components/map-nav";
import styles from "./mappages.module.css";
import { SiteTitle } from "app/components";

export const MapToaster = Toaster.create({
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
  mapstyle,
}: MapProps) {
  const initialState = {
    MapStyle: mapstyle,
    showMarkers: true,
    clickPnt: { lng: 0, lat: 0 },
    mounted: false,
  };
  useEffect(() => {
    setState({ ...state, mounted: true });
  }, []);
  const initialData = useAPIResult("/sample", { all: true });

  const initialViewport = {
    latitude,
    longitude,
    zoom,
    width,
    height,
    transitionInterpolator: null,
    transitionDuration: null,
  };

  const [state, setState] = useState(initialState);
  const [viewport, setViewport] = useState(initialViewport);

  // getting url hash to set location from
  let firstWindowHash = window.location.hash;

  // function that parses {zoom, latitude, longitude} from url hash
  function setLocationFromHash(hash) {
    if (hash == null) {
      ({ hash } = window.location);
    }
    const s = hash.slice(1);
    const v = s.split("/");
    if (v.length !== 3) {
      return {};
    }
    const [zoom, latitude, longitude] = v.map((d) => parseFloat(d));
    setViewport({ ...viewport, zoom, latitude, longitude });
  }

  useEffect(() => {
    const onMap = window.location.pathname == "/map";
    if (!onMap) {
      MapToaster.clear();
    }
    console.log(onMap);
  }, [window.location.pathname]);

  useEffect(() => {
    if (firstWindowHash !== "") {
      setLocationFromHash(firstWindowHash);
    }
  }, [firstWindowHash]);

  const mapRef = useRef();

  const bounds = mapRef.current
    ? mapRef.current.getMap().getBounds().toArray().flat()
    : null;

  const toggleShowMarkers = () => {
    setState({ ...state, showMarkers: !state.showMarkers });
  };

  const chooseMapStyle = (props) => {
    setState({ ...state, MapStyle: props });
  };

  const changeViewport = ({ expansionZoom, longitude, latitude }) => {
    setViewport({
      ...viewport,
      longitude: longitude,
      latitude: latitude,
      zoom: expansionZoom,
      transitionInterpolator: new FlyToInterpolator({
        speed: 1,
      }),
      transitionDuration: "auto",
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
        {on_map && (
          <Navbar>
            <Navbar.Group className={styles.mapNavbar}>
              <Navbar.Heading>
                <SiteTitle />
              </Navbar.Heading>
              <Navbar.Divider />
              <MapNav />
              <LayerMenu
                hide={hide_filter}
                MapStyle={state.MapStyle}
                chooseMapStyle={chooseMapStyle}
                //mapstyles={mapStyles}
                showMarkers={state.showMarkers}
                toggleShowMarkers={toggleShowMarkers}
              ></LayerMenu>
              <FilterMenu hide={hide_filter} on_map={on_map}></FilterMenu>
            </Navbar.Group>
          </Navbar>
        )}
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
            if (state.mounted) {
              setViewport(viewport);
            }
          }}
          ref={mapRef}
        >
          {state.clickPnt.lng && on_map && (
            <Marker
              latitude={state.clickPnt.lat}
              longitude={state.clickPnt.lng}
              offsetLeft={-5}
              offsetTop={-10}
            >
              <Icon icon="map-marker" color="black"></Icon>
            </Marker>
          )}

          {state.showMarkers ? (
            <MarkerCluster
              data={initialData}
              viewport={viewport}
              changeViewport={changeViewport}
              bounds={bounds}
            ></MarkerCluster>
          ) : null}
        </MapGl>
      </div>
    </div>
  );
}
