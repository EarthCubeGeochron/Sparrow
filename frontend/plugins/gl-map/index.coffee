import ReactMapGL from 'react-map-gl'
import h from 'react-hyperscript'

GLMap = (props)->
  h Map, null, (
    h ReactMapGL, {
      props...
      style: "mapbox://styles/mapbox/outdoors-v9"
    }
  )

export {GLMap}
