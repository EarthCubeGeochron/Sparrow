import h from '@macrostrat/hyper'
import T from 'prop-types'
import {ContextMap, StaticMarker} from 'app/components'
import bbox from '@turf/bbox'
import WebMercatorViewport from 'viewport-mercator-project'

ProjectMap = (props)->
  {width, height, samples, padding, minExtent} = props
  return null unless samples?
  locatedSamples = samples.filter (d)->d.geometry?
  return null unless locatedSamples.length > 0
  padding ?= 50
  minExtent ?= 0.2 # In degrees
  width ?= 400
  height ?= 300
  vp = new WebMercatorViewport {width, height}
  {samples} = props
  coordinates = locatedSamples
    .map (d)-> d.geometry.coordinates
  return null unless coordinates.length
  feature = {
    type: 'Feature'
    geometry: {
      type: 'MultiPoint',
      coordinates
    }}
  box = bbox(feature)
  bounds = [box.slice(0,2), box.slice(2,4)]
  console.log(bounds)
  res = vp.fitBounds(bounds, {padding, minExtent})
  {latitude, longitude, zoom} = res
  center = [longitude, latitude]

  h ContextMap, {
    className: 'project-context-map'
    center
    zoom
    width
    height
  }, locatedSamples.map (d)->
    [longitude, latitude] = d.geometry.coordinates
    console.log longitude, latitude
    h StaticMarker, {latitude, longitude}

export {ProjectMap}
