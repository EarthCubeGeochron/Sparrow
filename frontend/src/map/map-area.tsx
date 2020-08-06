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
import { mapStyle } from "./MapStyle";
import { Component } from "react";
import h, { compose } from "@macrostrat/hyper";
import useSuperCluster from "use-supercluster";
import {
  Tooltip,
  Popover,
  Button,
  Menu,
  Position,
  MenuItem,
  Intent,
  MenuDivider,
} from "@blueprintjs/core";
import classNames from "classnames";
import "./cluster.css";
import {
  APIContext,
  APIActions,
  QueryParams,
  APIHookOpts,
} from "@macrostrat/ui-components";
import { Link } from "react-router-dom";
import { INTENT_DANGER } from "@blueprintjs/core/lib/esm/common/classes";

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

function MapPanel({
  width = "50vw",
  height = "500px",
  latitude = 0,
  longitude = 0,
  zoom = 1,
  mapstyle = "mapbox://styles/mapbox/outdoors-v9",
}) {
  const [markers, setMarkers] = useState([]);
  const [viewport, setViewport] = useState({
    latitude,
    longitude,
    zoom,
    width,
    height,
  });
  const [MapStyle, setMapStyle] = useState(mapstyle);
  const [showMarkers, setShowMarkers] = useState(true);

  const initialMapStyle = "mapbox://styles/mapbox/outdoors-v9";

  const mapRef = useRef();

  const initialData = useAPIResult("/sample", { all: true });

  useEffect(() => {
    // Set the data back to the initial data
    if (initialData == null) return;
    const markers = initialData.filter((d) => d.geometry != null);

    setMarkers(markers);
  }, [initialData]);

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

  const dropMenu = (
    <Menu>
      <MenuItem
        intent={MapStyle == mapStyle ? "primary" : null}
        icon={MapStyle == mapStyle ? "tick" : null}
        onClick={() => setMapStyle(mapStyle)}
        text="Bedrock Geology"
      />
      <MenuItem
        intent={MapStyle == initialMapStyle ? "primary" : null}
        icon={MapStyle == initialMapStyle ? "tick" : null}
        onClick={() => setMapStyle(initialMapStyle)}
        text="Standard Satelite"
      />
      <MenuItem text="Topographic" />
      <MenuDivider />
      <MenuItem
        label={showMarkers ? "On" : "Off"}
        intent={showMarkers ? "warning" : null}
        onClick={() => setShowMarkers(!showMarkers)}
        text="Markers"
      />
    </Menu>
  );

  return (
    <div className="map-container">
      <div className="layer-button">
        <Popover content={dropMenu} position={Position.BOTTOM}>
          <Tooltip content="Change Map">
            <Button icon="layers"></Button>
          </Tooltip>
        </Popover>
      </div>
      <div>
        <MapGl
          mapStyle={MapStyle}
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
            if (showMarkers === true) {
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
                    <Tooltip content={cluster.properties.Sample_name}>
                      <Button className="bp3-minimal" icon="map-marker" />
                    </Tooltip>
                  </Popover>
                </Marker>
              );
            }
          })}
        </MapGl>
      </div>
    </div>
  );
}

export { MapPanel };
