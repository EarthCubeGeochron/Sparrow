/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {InteractiveMap, Marker, Popup} from 'react-map-gl';
import h from 'react-hyperscript';
import {Component} from 'react';
import {APIResultView} from '@macrostrat/ui-components';
import "./mapbox-gl.css";
import styled from '@emotion/styled';
import {Popover, Text} from '@blueprintjs/core';

const MarkerInner = styled.span`\
display: block;
background-color: #ad99ff;
width: 10px;
height: 10px;
border: 1px solid #634dbf;
border-radius: 5px;
pointer-events: all;\
`;

const PopoverMarker = props => h(Popover, [
  h(MarkerInner,
  h('div', [
    h('h4', props.name)
  ]))
]);

class MarkerOverlay extends Component {
  render() {
    const route = "/sample";
    const params = {geometry: "%"};
    return h(APIResultView, {route, params}, data=> {
      if (data == null) { return null; }
      if (!Array.isArray(data)) { return null; }
      const markers = data.map(function(d){
        const {geometry, ...rest} = d;
        const {
          coordinates
        } = JSON.parse(d.geometry);
        return { coordinates, ...rest};});

      return h(markers.map(function(d){
          const {coordinates} = d;
          console.log(coordinates);
          const [longitude, latitude] = coordinates;
          return h(Marker, {latitude, longitude, offsetLeft: -5, offsetTop: -5}, (
            h(PopoverMarker, d)
          ));
      })
      );
    });
  }
}

class GLMap extends Component {
  constructor(props){
    super(props);
    this.onViewportChange = this.onViewportChange.bind(this);
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
    console.log(accessToken);
    return h(InteractiveMap, {
      ...rest,
      mapStyle: "mapbox://styles/mapbox/outdoors-v9",
      mapboxApiAccessToken:  accessToken,
      width: 800,
      height: 400,
      ...viewport,
      onViewportChange: this.onViewportChange
    }, (
      h(MarkerOverlay)
    ));
  }

  onViewportChange(viewport){
    return this.setState({viewport});
  }
}

export {GLMap};
