/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {InteractiveMap} from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import {Component} from 'react';
import {APIResultView} from '@macrostrat/ui-components';
import {StaticMarker} from 'app/components';
import {ErrorBoundary} from 'app/util';
import h, {compose} from '@macrostrat/hyper';

const ErrorTolerantAPI = compose(ErrorBoundary, APIResultView);

// Should add raster hillshading styles to map...
// https://docs.mapbox.com/mapbox-gl-js/example/hillshade/

const SampleOverlay = function(props){
  const route = "/sample";
  const params = {geometry: "%", all: true};
  return h(ErrorTolerantAPI, {route, params}, function(data){
    const markerData = data.filter(d => d.geometry != null);
    return h(markerData.map(function(d){
      const [longitude, latitude] = d.geometry.coordinates;
      return h(StaticMarker, {latitude, longitude});}));
});
};

class MapPanel extends Component {
  constructor(props){
    {
      // Hack: trick Babel/TypeScript into allowing this before super.
      if (false) { super(); }
      let thisFn = (() => { return this; }).toString();
      let thisName = thisFn.match(/return (?:_assertThisInitialized\()*(\w+)\)*;/)[1];
      eval(`${thisName} = this;`);
    }
    this.onViewportChange = this.onViewportChange.bind(this);
    super(props);
    this.firstWindowHash = window.location.hash;
    this.state = {
      viewport: {
        latitude: 43.6150,
        longitude: -140.2023,
        zoom: 2
      }
    };
  }

  render() {
    const {accessToken, ...rest} = this.props;
    const {viewport} = this.state;

    return h(InteractiveMap, {
      ...rest,
      mapStyle: "mapbox://styles/mapbox/outdoors-v9",
      mapboxApiAccessToken: process.env.MAPBOX_API_TOKEN,
      width: "100vw",
      height: "100vh",
      mapOptions: {
        hash: true
      },
      ...viewport,
      onViewportChange: this.onViewportChange
    }, [
      h(SampleOverlay)
    ]);
  }

  setLocationFromHash(hash){
    if (hash == null) { ({
      hash
    } = window.location); }
    const s = hash.slice(1);
    const v = s.split("/");
    if (v.length !== 3) { return {}; }
    const [zoom, latitude, longitude] = v.map(d => parseFloat(d));
    return this.setState({viewport: {zoom, latitude, longitude}});
  }

  componentDidMount() {
    // We would do this in componentDidMount,
    // but there is a flash of a bad hash from the
    // main map component.
    this.setLocationFromHash(this.firstWindowHash);
    return delete this.firstWindowHash;
  }

  onViewportChange(viewport){
    return this.setState({viewport});
  }
}

export {MapPanel};
