import * as React from "react";
import { useState, useEffect } from "react";
import { useAPIResult } from "./APIResult";
import useSuperCluster from "use-supercluster";
import classNames from "classnames";
import { Link } from "react-router-dom";
import "../cluster.css";
import { Tooltip, Popover, Button, Intent } from "@blueprintjs/core";
import { Marker, FlyToInterpolator } from "react-map-gl";

// This component controls the State and the UI for the markers and the markercluster

export function MarkerCluster({ viewport, changeViewport, bounds, data }) {
  const [markers, setMarkers] = useState([]);
  const initialData = data;
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

  const { clusters, supercluster } = useSuperCluster({
    points,
    zoom: viewport.zoom,
    bounds,
    options: { radius: 75, maxZoom: 5 },
  });

  const markerClicked = (e) => {
    return console.log(e);
  };

  return (
    <div>
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
              captureClick={true}
              captureDoubleClick={true}
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
                  changeViewport({ expansionZoom, longitude, latitude });
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
            offsetLeft={-15}
            offsetTop={-20}
            captureClick={true}
            captureDoubleClick={true}
          >
            <Popover
              content={
                <Link to={`/catalog/sample/${cluster.properties.id}`}>
                  <Button>Go to Sample {cluster.properties.Sample_name}</Button>
                </Link>
              }
            >
              <Tooltip content={cluster.properties.Sample_name}>
                <Button
                  minimal={true}
                  className="mrker-btn"
                  icon="map-marker"
                />
              </Tooltip>
            </Popover>
          </Marker>
        );
      })}
    </div>
  );
}
