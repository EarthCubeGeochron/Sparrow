import * as React from "react";
import { useState, useRef, useEffect } from "react";
import MapGl, { FlyToInterpolator, Marker, Source, Layer } from "react-map-gl";
import h, { compose } from "@macrostrat/hyper";
import { Toaster, Position, Icon, Navbar } from "@blueprintjs/core";
import "./cluster.css";
import { LayerMenu } from "./components/LayerMenu";
import { MapToast } from "./components/MapToast";
import { MapNav } from "./components/map-nav";
import styles from "./module.styl";
import { ShortSiteTitle } from "~/components";
import { apiBaseURL, mapboxAPIToken } from "~/env";
import { MapPanel } from "./map-panel";
import { MapboxMapProvider } from "@macrostrat/mapbox-react";
import { getMapboxStyle, mergeStyles } from "@macrostrat/mapbox-utils";

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
  style?: any;
}

export function _MapArea({
  on_map,
  hide_filter = false,
  width = "50vw",
  height = "500px",
  latitude = 0,
  longitude = 0,
  zoom = 0.5,
  login = false,
  style,
}: MapProps) {
  const initialState = {
    style,
    showMarkers: true,
    clickPnt: { lng: 0, lat: 0 },
    mounted: false,
  };
  useEffect(() => {
    setState({ ...state, mounted: true });
  }, []);

  useEffect(() => {
    setState((prevState) => ({ ...prevState, style }));
  }, [style]);

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
  const [resolvedStyle, setResolvedStyle] = useState(null);

  const overlays = {
    sources: {
      "sparrow-data": {
        type: "vector",
        tiles: [`${apiBaseURL}/api/v3/samples/{z}/{x}/{y}.pbf`],
        maxZoom: 12,
      },
    },
    layers: [
      {
        id: "samples",
        type: "circle",
        source: "sparrow-data",
        "source-layer": "default",
        paint: {
          // Circle radius varying by 'n' property
          "circle-radius": [
            "interpolate",
            ["exponential", 1.2],
            ["get", "n"],
            1,
            2,
            20,
            8,
          ],
          "circle-color": "#ff0000",
          "circle-opacity": 0.5,
        },
      },
    ],
  };

  useEffect(() => {
    buildMapStyle(state.style, overlays).then(setResolvedStyle);
  }, [state.style]);

  // This makes sure the maptoasters are cleared
  // when the component unmounts
  useEffect(() => {
    return () => MapToaster.clear();
  }, []);

  const toggleShowMarkers = () => {
    setState({ ...state, showMarkers: !state.showMarkers });
  };

  const chooseMapStyle = (props) => {
    setState({ ...state, style: props });
  };

  const mapClicked = (e, map) => {
    let res = map.queryRenderedFeatures(e.point, {
      layers: ["samples"],
    });

    console.log(
      "Samples:",
      res.map((d) => d.properties)
    );

    setState({
      ...state,
      clickPnt: e.lngLat,
    });
    if (hide_filter == false) {
      return MapToaster.show({
        message: h(MapToast, {
          login: login,
          mapstyle: state.style,
          ...e.lngLat,
        }),
        timeout: 0,
      });
    }
  };

  return h("div.map-container", [
    // Weird
    h("div.layer-button", [
      h.if(on_map)(MapNavbar, {
        chooseMapStyle,
        toggleShowMarkers,
        MapStyle: state.style,
        showMarkers: state.showMarkers,
      }),
    ]),
    h(MapPanel, {
      style: resolvedStyle,
      accessToken: mapboxAPIToken,
      onClick: mapClicked,
    }),
  ]);
}

async function buildMapStyle(baseStyle: any, overlays: any) {
  const s = await getMapboxStyle(baseStyle, { access_token: mapboxAPIToken });
  return mergeStyles(s, overlays);
}

function OldMapPanel() {
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

  return h("div", [
    h(
      MapGl,
      {
        // onClick(e) {
        //   mapClicked(e);
        // },
        mapStyle: state.MapStyle,
        mapboxApiAccessToken: mapboxAPIToken,
        ...viewport,
        onViewportChange(viewport) {
          if (state.mounted) {
            setViewport(viewport);
          }
        },
        //ref: mapRef,
      },
      [
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
  ]);
}

function MapNavbar({
  hide_filter,
  mapStyle,
  chooseMapStyle,
  showMarkers,
  toggleShowMarkers,
}) {
  return h(Navbar, { className: styles["map-navbar"] }, [
    h(Navbar.Group, { className: styles["map-navbar-inner"] }, [
      h(Navbar.Heading, h("h1", h(ShortSiteTitle))),
      h(Navbar.Divider),
      h(MapNav),
      h(LayerMenu, {
        hide: hide_filter,
        mapStyle,
        chooseMapStyle,
        showMarkers,
        toggleShowMarkers,
      }),
    ]),
  ]);
}

export const MapArea = compose(MapboxMapProvider, _MapArea);
