import React, {Component} from 'react'
import h from 'react-hyperscript'
import {
  ComposableMap,
  ZoomableGlobe,
  Geographies,
  Geography,
  Graticule,
  Markers,
  Marker,
} from "react-simple-maps"
import worldMap from './assets/land-110m.json'
import {APIResultView} from '@macrostrat/ui-components'
import {Colors} from '@blueprintjs/core'

class MapComponent extends Component
  render: ->
    {markers} = @props
    markers ?= []
    style = {
      fill: '#e9fcea',
      stroke: Colors.GRAY5,
      strokeWidth: 0.75,
      outline: "none",
    }

    return (
      <div>
        <ComposableMap
          projection="orthographic"
          projectionConfig={{
            scale: 400,
          }}
          width={820}
          height={820}
          style={{
            width: "100%",
            height: "auto",
            maxHeight: "500px"
          }} >
          <ZoomableGlobe
            center={[ -120, 35 ]}
            fill="#afe6f0"
            stroke="#eceff1"
            style={{cursor: "move"}} >
            <circle cx={410} cy={410} r={400} fill="#afe6f0" stroke="#888888" />
            <Geographies geography={worldMap} disableOptimization>
              {(geographies, projection) =>
                  geographies.map (geography, i) =>
                    <Geography
                      key={i}
                      geography={geography}
                      projection={projection}
                      style={{
                        default: style,
                        hover: style
                        pressed: style
                      }}
                    />
              }
            </Geographies>
            <Markers>
              {markers.map (marker, i) =>
                <Marker
                  key={i}
                  marker={marker}
                  style={{
                    default: { fill: "#ad99ff" },
                    hover: { fill: "#634dbf" },
                    pressed: { fill: "#FF5722" },
                    hidden: { opacity: 0 }
                  }}
                  >
                  <circle
                    cx={0}
                    cy={0}
                    r={10}
                    style={{
                      stroke: "#634dbf",
                      strokeWidth: 3,
                      opacity: 0.9,
                    }}
                  />
                </Marker>
              }
            </Markers>
          </ZoomableGlobe>
        </ComposableMap>
      </div>
    )


class SampleMap extends Component
  render: ->
    route = "/sample"
    params = {geometry: "%"}
    h APIResultView, {route, params}, (data)=>
      markers = data.map (d)->
        {
          coordinates: JSON.parse(d.geometry).coordinates
          name: d.id
        }

      h 'div', [
        h 'h4', "#{data.length} measurements have been linked to their geologic metadata"
        h MapComponent, {markers}
      ]

export {MapComponent, SampleMap}
