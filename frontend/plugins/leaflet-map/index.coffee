import { Map } from 'react-leaflet'
import MapboxGlLayer from '@mongodb-js/react-mapbox-gl-leaflet'
import h from 'react-hyperscript'

LeafletMap = (props)->
  h Map, null, (
    h MapboxGlLayer, {
      props...
      style: "mapbox://styles/mapbox/outdoors-v9"
    }
  )

export {LeafletMap}
