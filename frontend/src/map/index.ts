import {
  Menu,
  MenuItem,
  Popover,
  Tooltip,
  Icon,
  Button,
  Collapse,
} from "@blueprintjs/core";
// @ts-ignore
import { hyperStyled, classed } from "@macrostrat/hyper";
// @ts-ignore
import styles from "./module.styl";
import { SiteTitle } from "app/components";
import { CatalogNavLinks } from "../admin";
import { AuthStatus } from "app/auth";
import { MapPanel } from "./map-area";
import { HashLink } from "react-router-hash-link";
import { Link } from "react-router-dom";
import "./mappages.modules.css";
import { useToggle } from "./components/APIResult";

const h = hyperStyled(styles);

const MapNavbar = function(props) {
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
  return h("div.map-home", [
    h("div.mapHome", [h(MapPanel, { width: "750px", hide_filter: true })]),
    h("div.map-butn", [
      h(
        Tooltip,
        { content: "Go to Map" },
        h(Link, { to: "/map" }, h(Button, { icon: "maximize" }))
      ),
    ]),
  ]);
};

const MapPage = (props) => {
  return h("div.map-page", [
    h(MapPanel, {
      on_map: false,
      hide_filter: false,
      width: "100vw",
      height: "100vh",
    }),
  ]);
};

const LocationLink = function(props) {
  const { zoom, latitude, longitude, children, ...rest } = props;
  const link = `/map#${zoom}/${latitude}/${longitude}`;
  return link;
};

const MapLink = function(props) {
  const { zoom, latitude, longitude, children, ...rest } = props;
  return h(
    HashLink,
    { to: `/map#${zoom}/${latitude}/${longitude}`, ...rest },
    children
  );
};

export { MapPage, MapLink, MapHome };
