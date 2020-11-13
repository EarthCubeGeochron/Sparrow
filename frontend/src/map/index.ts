import { Menu, MenuItem, Tooltip, Button } from "@blueprintjs/core";
// @ts-ignore
import { hyperStyled } from "@macrostrat/hyper";
// @ts-ignore
//import styles from "./module.styl";
import { SiteTitle } from "app/components";
import { MapPanel } from "./map-area";
import { HashLink } from "react-router-hash-link";
import { Link } from "react-router-dom";
import styles from "./module.styl";
import { useDarkMode } from "@macrostrat/ui-components";
import { useEffect, useState } from "react";

const h = hyperStyled(styles);

const MapNavbar = function (props) {
  const { children, ...rest } = props;
  return h(Menu, { className: "map-navbar", ...rest }, [
    h(MenuItem, {
      text: h("h1.site-title", null, [h(SiteTitle)]),
    }),
    h.if(children != null)(Menu.Divider),
    children,
  ]);
};

const MapHome = (props) => {
  const link = LocationLink(props);
  const [style, setStyle] = useState("");

  const { isEnabled } = useDarkMode();

  useEffect(() => {
    if (isEnabled) {
      setStyle("mapbox://styles/mapbox/dark-v10");
    }
    setStyle("mapbox://styles/mapbox/outdoors-v9");
  }, [isEnabled]);

  const StandMapMode = isEnabled
    ? "mapbox://styles/mapbox/dark-v10"
    : "mapbox://styles/mapbox/outdoors-v9";
  return h("div.map-home", [
    h("div.map-butn", [
      h(
        Tooltip,
        { content: "Go to Map" },
        h(Link, { to: "/map" }, h(Button, { icon: "maximize" }))
      ),
    ]),
    h("div.mapHome", [
      h(MapPanel, {
        width: "750px",
        hide_filter: true,
        mapstyle: StandMapMode,
      }),
    ]),
  ]);
};

const MapPage = (props) => {
  const { isEnabled } = useDarkMode();

  const StandMapMode = isEnabled
    ? "mapbox://styles/mapbox/dark-v10"
    : "mapbox://styles/mapbox/outdoors-v9";

  return h("div.map-page", [
    h(MapPanel, {
      on_map: true,
      hide_filter: false,
      width: "100vw",
      height: "100vh",
      mapstyle: StandMapMode,
    }),
  ]);
};

<<<<<<< HEAD
=======
const LocationLink = function (props) {
  const { zoom, latitude, longitude, children, ...rest } = props;
  const link = `/map#${zoom}/${latitude}/${longitude}`;
  return link;
};
>>>>>>> master

const MapLink = function (props) {
  const { zoom, latitude, longitude, children, ...rest } = props;
  return h(
    HashLink,
    { to: `/map#${zoom}/${latitude}/${longitude}`, ...rest },
    children
  );
};

export { MapPage, MapLink, MapHome };
