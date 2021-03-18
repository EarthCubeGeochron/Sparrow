import * as React from "react";
import { useState, useEffect } from "react";
import useSuperCluster from "use-supercluster";
import classNames from "classnames";
import { Link } from "react-router-dom";
import "../cluster.css";
import {
  Popover,
  Card,
} from "@blueprintjs/core";
import { Marker, FlyToInterpolator } from "react-map-gl";
import styles from "./components.module.css";

// This component controls the State and the UI for the markers and the markercluster

export function MarkerCluster({ viewport, changeViewport, bounds, data }) {
  const [markers, setMarkers] = useState([]);
  useEffect(() => {
    // Set the data back to the initial data
    if (data == null) return;
    const markers = data.map((markers) => ({
      type: "Feature",
      properties: {
        cluster: false,
        id: markers.id,
        Sample_name: markers.name,
        material: markers.material,
      },
      geometry: {
        type: "Point",
        coordinates: [
          markers.location.coordinates[0],
          markers.location.coordinates[1],
        ],
      },
    }));

    setMarkers(markers);
  }, [data]);

  const { clusters, supercluster } = useSuperCluster({
    points: markers,
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

        const clusterSize = Math.sqrt(5 * pointCount);

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
                  width: clusterSize,
                  height: clusterSize,
                  marginTop: -clusterSize / 2,
                  marginRight: -clusterSize / 2,
                }}
                onDoubleClick={(e) => {
                  e.stopPropagation();
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
            captureClick={true}
            captureDoubleClick={true}
          >
            <Popover
              inheritDarkTheme={false}
              content={
                <Link to={`/catalog/sample/${cluster.properties.id}`}>
                  <Card>
                    <div style={{ display: "flex", flexDirection: "column" }}>
                      <b>{cluster.properties.Sample_name}</b>
                      {cluster.properties.material && (
                        <i>{cluster.properties.material}</i>
                      )}
                    </div>
                  </Card>
                </Link>
              }
            >
              <div className={styles.markerButton} />
            </Popover>
          </Marker>
        );
      })}
    </div>
  );
}
