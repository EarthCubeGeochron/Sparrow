/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import { useEffect, useState } from "react";
import {
  Menu,
  MenuItem,
  Popover,
  Tooltip,
  Icon,
  Button,
} from "@blueprintjs/core";
import { hyperStyled, classed } from "@macrostrat/hyper";
import styles from "./module.styl";
import { SiteTitle } from "app/components/navbar";
import { CatalogNavLinks } from "../admin";
import { AuthStatus } from "app/auth";
import { MapPanel } from "./map-area";
import { HashLink } from "react-router-hash-link";

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

const MapHomePanel = () => {
  return (
    <div>
      <Tooltip content={<h4>Go to Map</h4>}>
        <Button icon="maximize"></Button>
      </Tooltip>
      <MapPanel />
    </div>
  );
};

const MapPage = (props) =>
  h("div.map-page", [
    h(MapNavbar, [
      h(CatalogNavLinks),
      h(Menu.Divider),
      h(AuthStatus, { large: false }),
    ]),
    h(MapPanel, {
      className: "main-map",
      accessToken: process.env.MAPBOX_API_TOKEN,
    }),
  ]);

const MapLink = function (props) {
  const { zoom, latitude, longitude, children, ...rest } = props;
  return h(
    HashLink,
    { to: `/map#${zoom}/${latitude}/${longitude}`, ...rest },
    children
  );
};

export { MapPage, MapLink, MapHomePanel };
