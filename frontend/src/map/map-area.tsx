import * as React from "react";
import { useState, useRef, useEffect } from "react";
import MapGl, { FlyToInterpolator, Marker, Source, Layer } from "react-map-gl";
import h from "@macrostrat/hyper";
import { Toaster, Position, Icon, Navbar } from "@blueprintjs/core";
import "./cluster.css";
import { LayerMenu } from "./components/LayerMenu";
import { MapToast } from "./components/MapToast";
import { MapNav } from "./components/map-nav";
import styles from "./module.styl";
import { ShortSiteTitle } from "~/components";

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
  login?: boolean;
  mapstyle?: any;
}

export function MapPanel({
  on_map,
  hide_filter = false,
  width = "50vw",
  height = "500px",
  latitude = 0,
  longitude = 0,
  zoom = 0.5,
  login = false,
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

  useEffect(() => {
    setState((prevState) => {
      return { ...prevState, MapStyle: mapstyle };
    });
  }, [mapstyle]);

  //changeStateOnParams(params, setData);

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

  // This makes sure the maptoasters are cleared
  // when the component unmounts
  useEffect(() => {
    return () => MapToaster.clear();
  }, []);

  useEffect(() => {
    if (firstWindowHash !== "") {
      setLocationFromHash(firstWindowHash);
    }
  }, [firstWindowHash]);

  const mapRef = useRef();

  const toggleShowMarkers = () => {
    setState({ ...state, showMarkers: !state.showMarkers });
  };

  const chooseMapStyle = (props) => {
    setState({ ...state, MapStyle: props });
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
            login={login}
            mapstyle={state.MapStyle}
            lng={e.lngLat[0]}
            lat={e.lngLat[1]}
          />
        ),
        timeout: 0,
      });
    }
  };

  return h("div.map-container", [
    h("div.layer-button", [
      h.if(on_map)(Navbar, { className: styles["map-navbar"] }, [
        <Navbar.Group className={styles["map-navbar-inner"]}>
          <Navbar.Heading>
            <h1>
              <ShortSiteTitle />
            </h1>
          </Navbar.Heading>
          <Navbar.Divider />
          <MapNav />
          <LayerMenu
            hide={hide_filter}
            MapStyle={state.MapStyle}
            chooseMapStyle={chooseMapStyle}
            showMarkers={state.showMarkers}
            toggleShowMarkers={toggleShowMarkers}
          ></LayerMenu>
        </Navbar.Group>,
      ]),
    ]),
    h("div", [
      h(
        MapGl,
        {
          onClick(e) {
            mapClicked(e);
          },
          mapStyle: state.MapStyle,
          mapboxApiAccessToken: process.env.MAPBOX_API_TOKEN,
          ...viewport,
          onViewportChange(viewport) {
            if (state.mounted) {
              setViewport(viewport);
            }
          },
          ref: mapRef,
        },
        [
          h(
            Source,
            {
              id: "sparrow-data",
              type: "vector",
              tiles: ["http://localhost:5002/api/v3/samples/{z}/{x}/{y}.pbf"],
            },
            [
              h(Layer, {
                "source-layer": "default",
                id: "point",
                type: "circle",
                paint: {
                  "circle-radius": 3,
                  "circle-color": "#007cbf",
                },
              }),
            ]
          ),
          h.if(state.clickPnt.lng && on_map)(
            Marker,
            {
              latitude: state.clickPnt.lat,
              longitude: state.clickPnt.lng,
              offsetLeft: -5,
              offsetTop: -10,
            },
            h(Icon, { icon: "map-marker", color: "black" })
          ),
        ]
      ),
    ]),
  ]);
}
