import {InteractiveMap} from 'react-map-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import {Component} from 'react'
import {APIResultView} from '@macrostrat/ui-components'
import {StaticMarker} from 'app/components'
import {ErrorBoundary} from 'app/util'
import h, {compose} from '@macrostrat/hyper'

ErrorTolerantAPI = compose(ErrorBoundary, APIResultView)

# mapStyle = {
#   version: 8,
#   sources: {
#     dem: {
#       type: "raster-dem",
#       url: "mapbox://mapbox.terrain-rgb"
#     }
#   },
#   layers: [
#     {
#       id: "hillshading",
#       source: "dem",
#       type: "hillshade"
#     }
#   ]
# }
# #-> waterway-river-canal-shadow

SampleOverlay = (props)->
  route = "/sample"
  params = {geometry: "%", all: true}
  h ErrorTolerantAPI, {route, params}, (data)->
    markerData = data.filter (d)->d.geometry?
    h markerData.map (d)->
      [longitude, latitude] = d.geometry.coordinates
      h StaticMarker, {latitude, longitude}

class MapPanel extends Component
  constructor: (props)->
    super props
    @firstWindowHash = window.location.hash
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

    h InteractiveMap, {
      rest...
      mapStyle: "mapbox://styles/mapbox/outdoors-v9"
      mapboxApiAccessToken: process.env.MAPBOX_API_TOKEN
      width: "100vw",
      height: "100vh",
      mapOptions: {
        hash: true
      }
      viewport...
      onViewportChange: @onViewportChange
    }, [
      h SampleOverlay
    ]

  setLocationFromHash: (hash)->
    hash ?= window.location.hash
    s = hash.slice(1)
    v = s.split("/")
    return {} unless v.length == 3
    [zoom, latitude, longitude] = v.map (d)->parseFloat(d)
    @setState {viewport: {zoom, latitude, longitude}}

  componentDidMount: ->
    # We would do this in componentDidMount,
    # but there is a flash of a bad hash from the
    # main map component.
    @setLocationFromHash(@firstWindowHash)
    delete @firstWindowHash

  onViewportChange: (viewport)=>
    @setState {viewport}

export {MapPanel}
