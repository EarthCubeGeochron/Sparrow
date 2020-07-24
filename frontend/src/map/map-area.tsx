/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import React, { useState, useEffect, useRef, useContext } from "react";
import MapGl, { Marker, FlyToInterpolator } from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { Component } from "react";
import h, { compose } from "@macrostrat/hyper";
import useSuperCluster from "use-supercluster";
import { Tooltip, Popover, Button } from "@blueprintjs/core";
import classNames from "classnames";
import "./cluster.css";
import {
  APIContext,
  APIActions,
  QueryParams,
  APIHookOpts,
} from "@macrostrat/ui-components";
import { Link } from "react-router-dom";

const useAPIResult = function <T>(
  route: string | null,
  params: QueryParams = {},
  opts: APIHookOpts | (<T, U = any>(arg: U) => T) = {}
): T {
  /* React hook for API results, pulled out of @macrostrat/ui-components.
  The fact that this works inline but the original hook doesn't suggests that we
  have overlapping React versions between UI-components and the main codebase.
  Frustrating. */
  const deps = [route, ...Object.values(params ?? {})];

  const [result, setResult] = useState<T | null>(null);

  if (typeof opts === "function") {
    opts = { unwrapResponse: opts };
  }

  const { debounce: _debounce, ...rest } = opts ?? {};
  let { get } = APIActions(useContext(APIContext));

  useEffect(() => {
    const getAPIData = async function () {
      if (route == null) {
        return setResult(null);
      }
      const res = await get(route, params, rest);
      return setResult(res);
    };
    getAPIData();
  }, deps);
  return result;
};

function MapPanel() {
  const [markers, setMarkers] = useState([]);
  const [viewport, setViewport] = useState({
    latitude: 0,
    longitude: 0,
    width: "100vw",
    height: "100vh",
    zoom: 1,
  });

  const mapRef = useRef();

  const initialData = useAPIResult("/sample", { all: true });

  useEffect(() => {
    // Set the data back to the initial data
    if (initialData == null) return;
    const markers = initialData.filter((d) => d.geometry != null);

    setMarkers(markers);
  }, [initialData]);

  // function setLocationFromHash() {
  //   let hash = window.location.hash;
  //   const s = hash.slice(1);
  //   const v = s.split("/");
  //   if (v.length !== 3) {
  //     return {};
  //   }
  //   const [zoom, latitude, longitude] = v.map((d) => parseFloat(d));
  //   return setViewport({ zoom, latitude, longitude });
  // }

  // useEffect(() => {
  //   setLocationFromHash();
  // }, []);

  const points = markers.map((markers) => ({
    type: "Feature",
    properties: {
      cluster: false,
      id: markers.id,
      Sample_name: markers.name,
      project_name: markers.project_name,
    },
    geometry: {
      type: "Point",
      coordinates: [
        markers.geometry.coordinates[0],
        markers.geometry.coordinates[1],
      ],
    },
  }));
  const bounds = mapRef.current
    ? mapRef.current.getMap().getBounds().toArray().flat()
    : null;

  const { clusters, supercluster } = useSuperCluster({
    points,
    zoom: viewport.zoom,
    bounds,
    options: { radius: 75, maxZoom: 5 },
  });

  return (
    <div>
      <MapGl
        mapStyle="mapbox://styles/mapbox/outdoors-v9"
        mapboxApiAccessToken={process.env.MAPBOX_API_TOKEN}
        {...viewport}
        onViewportChange={(viewport) => {
          setViewport(viewport);
        }}
        ref={mapRef}
      >
        {clusters.map((cluster) => {
          const [longitude, latitude] = cluster.geometry.coordinates;
          const {
            cluster: isCluster,
            point_count: pointCount,
          } = cluster.properties;

          const clusterClass = classNames({
            "cluster-marker": pointCount < 50,
            "cluster-markerGreen": pointCount >= 50 && pointCount < 100,
            "cluster-markerYellow": pointCount >= 100 && pointCount < 200,
            "cluster-markerRed": pointCount >= 200,
          });

          if (isCluster) {
            return (
              <Marker
                key={cluster.id}
                longitude={longitude}
                latitude={latitude}
              >
                <div
                  className={clusterClass}
                  style={{
                    width: `${20 + (pointCount / points.length) * 250}px`,
                    height: `${20 + (pointCount / points.length) * 250}px`,
                  }}
                  onClick={() => {
                    const expansionZoom = Math.min(
                      supercluster.getClusterExpansionZoom(cluster.id),
                      5
                    );
                    setViewport({
                      ...viewport,
                      longitude,
                      latitude,
                      zoom: expansionZoom,
                      transitionInterpolator: new FlyToInterpolator({
                        speed: 1,
                      }),
                      transitionDuration: "auto",
                    });
                  }}
                >
                  {pointCount}
                </div>
              </Marker>
            );
          }

          return (
            <Marker
              key={cluster.properties.id}
              latitude={latitude}
              longitude={longitude}
            >
              <Popover
                content={
                  <Link to={`/catalog/sample/${cluster.properties.id}`}>
                    <Button>
                      Go to Sample {cluster.properties.Sample_name}
                    </Button>
                  </Link>
                }
              >
                <Tooltip
                  content={
                    cluster.properties.Sample_name +
                    ": " +
                    cluster.properties.project_name
                  }
                >
                  <Button icon="circle" />
                </Tooltip>
              </Popover>
            </Marker>
          );
        })}
      </MapGl>
    </div>
  );
}

export { MapPanel };
