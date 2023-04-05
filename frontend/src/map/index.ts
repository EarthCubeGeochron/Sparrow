import { Menu, MenuItem, Tooltip, Button } from "@blueprintjs/core";
// @ts-ignore
import { hyperStyled } from "@macrostrat/hyper";
// @ts-ignore
//import styles from "./module.styl";
import { SiteTitle } from "app/components";
import { MapPanel } from "./map-panel";
import { HashLink } from "react-router-hash-link";
import { Link } from "react-router-dom";
import styles from "./module.styl";
import { useDarkMode, useElementSize } from "@macrostrat/ui-components";
import { useAuth } from "~/auth";
import { MapArea } from "./map-area";
import { useRef } from "react";

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
  const { isEnabled } = useDarkMode();
  const ref = useRef(null);
  const size = useElementSize(ref);

  const style = isEnabled
    ? "mapbox://styles/mapbox/dark-v10"
    : "mapbox://styles/mapbox/outdoors-v9";

  return h("div.map-home", { ref }, [
    h("div.map-butn", [
      h(
        Tooltip,
        { content: "Go to Map" },
        h(Link, { to: "/map" }, h(Button, { icon: "maximize", minimal: true }))
      ),
    ]),
    h(
      "div.homepage-map",
      {
        style: { height: size?.height ?? 0, width: size?.width ?? 0 },
      },
      [
        h(MapArea, {
          style,
        }),
      ]
    ),
  ]);
};

const MapPage = (props) => {
  const { isEnabled } = useDarkMode();

  const style = isEnabled
    ? "mapbox://styles/mapbox/dark-v10"
    : "mapbox://styles/mapbox/outdoors-v9";

  const { login } = useAuth();
  //console.log(login);

  return h("div.map-page", [
    h(MapArea, {
      on_map: true,
      hide_filter: false,
      className: "fullscreen-map",
      style,
      login,
    }),
  ]);
};

const LocationLink = function (props) {
  const { zoom, latitude, longitude, children, ...rest } = props;
  const link = `/map#${zoom}/${latitude}/${longitude}`;
  return link;
};

const MapLink = function (props) {
  const { zoom, latitude, longitude, children, ...rest } = props;
  return h(
    HashLink,
    { to: `/map#${zoom}/${latitude}/${longitude}`, ...rest },
    children
  );
};

export { MapPage, MapLink, MapHome };
