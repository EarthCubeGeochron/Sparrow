/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import React, { useState, useEffect, useRef } from "react";
import LandscapeIcon from "@material-ui/icons/Landscape";
import MapGl, {
  Marker,
  FlyToInterpolator,
} from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { Component } from "react";
import { useAPIResult, APIResultView } from "@macrostrat/ui-components";
//import { StaticMarker } from "app/components";
//import { ErrorBoundary } from "app/util";
import h, { compose } from "@macrostrat/hyper";
import useSuperCluster from "use-supercluster";
import { Tooltip, Popover, Button } from "@blueprintjs/core";
import classNames from "classnames";
import "./cluster.css";
//const ErrorTolerantAPI = compose(ErrorBoundary, APIResultView);

// Should add raster hillshading styles to map...
// https://docs.mapbox.com/mapbox-gl-js/example/hillshade/

// function SampleOverlay(props) {
//   const route = "/sample";
//   const params = { geometry: "%", all: true };
//   return (
//     <div>
//       <ErrorTolerantAPI route={route} params={params}>
//         {({data})=> {
//           const markerData = data.filter((d) => d.geometry != null);
//           return
//             markerData.map(({d})=> {
//             const [longitude, latitude] = d.geometry.coordinates;
//             return
//               <StaticMarker latitude={latitude} longitude={longitude}/>

//       </ErrorTolerantAPI>

//     </div>

// };

function MapPanel() {
  let hash = window.location.hash;
  const [markers, setMarkers] = useState([]);
  const [viewport, setViewport] = useState({
    latitude: 0,
    longitude: 0,
    width: "100vw",
    height: "100vh",
    zoom: 1,
  });

  const mapRef = useRef();

  // const data = useAPIResult("/sample");
  // console.log(data);

  const [selectedSample, setSelectedSample] = useState(null);

  useEffect(() => {
    getMarkers();
  }, []);

  async function getMarkers() {
    const response = await fetch(
      "https://sparrow-data.org/labs/wiscar/api/v1/sample?all=1"
    );
    const markers = await response.json();
    setMarkers(markers);
  }

  const mapMarkers = markers.filter((d) => d.geometry != null);

  const points = mapMarkers.map((markers) => ({
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
              <Popover content={cluster.properties.Sample_name}>
                  <Tooltip content={cluster.properties.Sample_name}>
                           <button className="mrker-btn">
                      <LandscapeIcon></LandscapeIcon>
                  </button>
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
