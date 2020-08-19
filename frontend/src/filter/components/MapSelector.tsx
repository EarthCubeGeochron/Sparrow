import * as React from "react";
import MapGl from "react-map-gl";

/**
 * This component is meant to be a location filter for data.
 * The end goal would be to make a polygon or box and it would filter
 * data down to those only in that area
 * */
export function MapSelector() {
  return <MapGl></MapGl>;
}
