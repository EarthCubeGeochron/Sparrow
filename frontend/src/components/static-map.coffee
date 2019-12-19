import {StaticMap as MGLStaticMap, Marker} from 'react-map-gl'
import {hyperStyled, classed} from '@macrostrat/hyper'
import {Component} from 'react'
import "mapbox-gl/dist/mapbox-gl.css"
import T from 'prop-types'
import styles from './module.styl'

h = hyperStyled(styles)

StaticMarker = (props)->
  {size, rest...} = props
  size ?= 10
  offsetLeft = offsetTop = -size/2
  h Marker, {offsetLeft, offsetTop, rest...}, (
    h 'span.map-marker.static', {style: {width: size, height: size}}
  )

StaticMarker.propTypes = {
  latitude: T.number.isRequired
  longitude: T.number.isRequired
}

class StaticMap extends Component
  @propTypes: {
    center: T.arrayOf(T.number).isRequired
    zoom: T.number.isRequired
    mapStyle: T.string
    width: T.number
    height: T.number
    accessToken: T.string
    markCenter: T.bool
  }
  @defaultProps: {
    accessToken: process.env.MAPBOX_API_TOKEN
    width: 200
    height: 150
    mapStyle: "mapbox://styles/mapbox/outdoors-v9"
    markCenter: false
  }

  render: ->
    {center, accessToken, markCenter, children, rest...} = @props
    [longitude, latitude] = center
    h MGLStaticMap, {
      latitude
      longitude
      mapboxApiAccessToken: accessToken
      attributionControl: false
      rest...
    }, [
      h.if(markCenter) StaticMarker, {latitude, longitude}
      children
    ]

ContextMap = classed(StaticMap, 'context-map')

SampleContextMap = (props)->
  h ContextMap, {props..., className: 'sample-context-map', markCenter: true}

export {StaticMarker, StaticMap, SampleContextMap, ContextMap}
