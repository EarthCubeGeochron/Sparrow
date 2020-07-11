/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import MapGl, { Marker, Popup, FlyToInterpolator } from "react-map-gl";
import h from "react-hyperscript";
import React, { useState } from "react";
import { APIResultView } from "@macrostrat/ui-components";
import "./mapbox-gl.css";
import styled from "@emotion/styled";
import { Popover, Text } from "@blueprintjs/core";
import Tippy from "@tippy.js/react";
import useSuperCluster from "use-supercluster";

const MarkerInner = styled.button`\
display: block;
background-color: #ad99ff;
width: 10px;
height: 10px;
border: 1px solid #634dbf;
border-radius: 5px;
pointer-events: all;\
`;

function MarkerOverlay() {
  const route = "/sample";
  const params = {
    geometry: "%",
  };
  return h(APIResultView, { route, params }, (data) => {
    if (data == null) {
      return null;
    }
    if (!Array.isArray(data)) {
      return null;
    }
    const markers = data.map(function (d) {
      const { geometry, ...rest } = d;
      const { coordinates } = JSON.parse(d.geometry);
      return { coordinates, ...rest };
    });

    return h(
      markers.map(function (d) {
        const { coordinates } = d;
        console.log(coordinates);
        const [longitude, latitude] = coordinates;
        return h(Marker, {
          latitude,
          longitude,
          offsetLeft: -5,
          offsetTop: -5,
        });
      })
    );
  });
}

function GLMap() {
  const [viewport, setViewport] = useState({
    viewport: {
      latitude: 43.615,
      longitude: -140.2023,
      zoom: 2,
    },
  });

  const onViewportChange = ({ viewport }) => {
    setViewport({ viewport });
  };

  const { accessToken, ...rest } = this.props;
  console.log(accessToken);
  return (
    <MapGl
      {...rest}
      mapStyle={"mapbox://styles/mapbox/outdoors-v9"}
      mapboxApiAccessToken={accessToken}
      width="800"
      height="400"
      {...viewport}
      onViewportChange={onViewportChange}
    ></MapGl>
  );
}

export { GLMap };
