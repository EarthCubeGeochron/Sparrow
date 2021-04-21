/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import h from "@macrostrat/hyper";
import { useState } from "react";
import { ContextMap, StaticMarker } from "app/components";
import bbox from "@turf/bbox";
import WebMercatorViewport from "viewport-mercator-project";
import { MapLink } from "~/map";

const ProjectMap = function (props) {
  let { width, height, samples, padding, minExtent, hoverID } = props;
  if (samples == null) {
    return null;
  }
  const locatedSamples = samples.filter((d) => d.location != null);
  if (!(locatedSamples.length > 0)) {
    return null;
  }
  if (padding == null) {
    padding = 50;
  }
  if (minExtent == null) {
    minExtent = 0.2;
  } // In degrees
  if (width == null) {
    width = 400;
  }
  if (height == null) {
    height = 300;
  }
  const vp = new WebMercatorViewport({ width, height });
  ({ samples } = props);
  const coordinates = locatedSamples.map((d) => d.location.coordinates);
  if (!coordinates.length) {
    return null;
  }
  const feature = {
    type: "Feature",
    geometry: {
      type: "MultiPoint",
      coordinates,
    },
  };
  const box = bbox(feature);
  const bounds = [box.slice(0, 2), box.slice(2, 4)];
  const res = vp.fitBounds(bounds, { padding, minExtent });
  let { latitude, longitude, zoom } = res;
  const center = [longitude, latitude];

  return h(MapLink, { zoom, latitude, longitude }, [
    h(
      ContextMap,
      {
        className: "project-context-map",
        center,
        zoom,
        width,
        height,
      },
      locatedSamples.map(function (d) {
        const { id } = d;
        [longitude, latitude] = d.location.coordinates;
        return h(StaticMarker, { latitude, longitude, id, hoverID });
      })
    ),
  ]);
};

export { ProjectMap };
