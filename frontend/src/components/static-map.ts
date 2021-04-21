import { StaticMap as MGLStaticMap, Marker } from "react-map-gl";
import { hyperStyled, classed } from "@macrostrat/hyper";
import { Component } from "react";
import T from "prop-types";
import styles from "./module.styl";

const h = hyperStyled(styles);

const StaticMarker = function (props) {
  let offsetTop;
  let { size, id, hoverID, ...rest } = props;
  if (size == null) {
    size = 10;
  }
  const offsetLeft = (offsetTop = -size / 2);

  const className =
    id == hoverID ? "map-marker.static.match" : "map-marker.static";

  return h(
    Marker,
    { offsetLeft, offsetTop, ...rest },
    h(`span.${className}`, { style: { width: size, height: size } })
  );
};

StaticMarker.propTypes = {
  latitude: T.number.isRequired,
  longitude: T.number.isRequired,
};

class StaticMap extends Component {
  static initClass() {
    this.propTypes = {
      center: T.arrayOf(T.number).isRequired,
      zoom: T.number.isRequired,
      mapStyle: T.string,
      width: T.number,
      height: T.number,
      accessToken: T.string,
      markCenter: T.bool,
    };
    this.defaultProps = {
      accessToken: process.env.MAPBOX_API_TOKEN,
      width: 200,
      height: 150,
      mapStyle: "mapbox://styles/mapbox/outdoors-v9",
      markCenter: false,
    };
  }

  render() {
    const { center, accessToken, markCenter, children, ...rest } = this.props;
    const [longitude, latitude] = center;
    return h(
      MGLStaticMap,
      {
        latitude,
        longitude,
        mapboxApiAccessToken: accessToken,
        attributionControl: false,
        ...rest,
      },
      [h.if(markCenter)(StaticMarker, { latitude, longitude }), children]
    );
  }
}
StaticMap.initClass();

const ContextMap = classed(StaticMap, "context-map");

const SampleContextMap = (props) =>
  h(ContextMap, {
    ...props,
    className: "sample-context-map",
    markCenter: true,
  });

export { StaticMarker, StaticMap, SampleContextMap, ContextMap };
