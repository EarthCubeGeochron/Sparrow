import {InteractiveMap} from 'react-map-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import h from 'react-hyperscript'
import {Component} from 'react'
import {APIResultView} from '@macrostrat/ui-components'

class MapPanel extends Component
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
    h InteractiveMap, {
      rest...
      mapStyle: "mapbox://styles/mapbox/outdoors-v9"
      mapboxApiAccessToken: process.env.MAPBOX_API_TOKEN
      width: "100vw",
      height: "100vh",
      viewport...
      onViewportChange: @onViewportChange
    }

  onViewportChange: (viewport)=>
    @setState {viewport}

export {MapPanel}
