import {InteractiveMap, Marker, Popup} from 'react-map-gl'
import h from 'react-hyperscript'
import {Component} from 'react'
import {APIResultView} from '@macrostrat/ui-components'
import "./mapbox-gl.css"
import styled from '@emotion/styled'
import {Popover, Text} from '@blueprintjs/core'

MarkerInner = styled.span"""
display: block;
background-color: #ad99ff;
width: 10px;
height: 10px;
border: 1px solid #634dbf;
border-radius: 5px;
pointer-events: all;
"""

PopoverMarker = (props)->
  h Popover, [
    h MarkerInner,
    h 'div', [
      h 'h4', props.name
    ]
  ]

class MarkerOverlay extends Component
  render: ->
    route = "/sample"
    params = {geometry: "%"}
    h APIResultView, {route, params}, (data)=>
      return null unless data?
      return null unless Array.isArray(data)
      markers = data.map (d)->
        {geometry, rest...} = d
        coordinates = JSON.parse(d.geometry).coordinates
        { coordinates, rest...}

      h markers.map (d)->
          {coordinates} = d
          console.log coordinates
          [longitude, latitude] = coordinates
          h Marker, {latitude, longitude, offsetLeft: -5, offsetTop: -5}, (
            h PopoverMarker, d
          )

class GLMap extends Component
  constructor: (props)->
    super props
    @state = {
      viewport: {
        latitude: 43.6150
        longitude: -140.2023,
        zoom: 2
      }
    }

  render: ->
    {accessToken, rest...} = @props
    {viewport} = @state
    console.log accessToken
    h InteractiveMap, {
      rest...
      mapStyle: "mapbox://styles/mapbox/outdoors-v9"
      mapboxApiAccessToken:  accessToken
      width: 800,
      height: 400,
      viewport...
      onViewportChange: @onViewportChange
    }, (
      h MarkerOverlay
    )

  onViewportChange: (viewport)=>
    @setState {viewport}

export {GLMap}
