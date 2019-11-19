import {Menu, MenuItem, Popover} from '@blueprintjs/core'
import {hyperStyled, classed} from '@macrostrat/hyper'
import styles from './module.styl'
import {SiteTitle} from 'app/components/navbar'
import {CatalogNavLinks} from '../admin'
import {AuthStatus} from 'app/auth'
import {MapPanel} from './map-area'
import {ErrorBoundary} from 'app/util'
import {APIResultView} from '@macrostrat/ui-components'
import {StaticMarker} from 'app/components'

h = hyperStyled(styles)

MapNavbar = (props)->
  {children, rest...} = props
  h Menu, {className: 'map-navbar', rest...}, [
    h MenuItem, {
      text: h 'h1.site-title', null, [
        h SiteTitle
      ]
    }
    h.if(children?) Menu.Divider
    children
  ]

SampleOverlay = ->
  route = "/sample"
  params = {geometry: "%", all: true}
  h APIResultView, {route, params}, (data)=>
    markerData = data.filter (d)->d.geometry?
    h markerData.map (d)->
      [longitude, latitude] = d.geometry.coordinates
      h StaticMarker, {latitude, longitude}


MapPage = (props)->
  h 'div.map-page', [
    h MapNavbar, [
      h CatalogNavLinks
      h Menu.Divider
      h AuthStatus, {large: false}
    ]
    h MapPanel, {
      className: 'main-map',
      accessToken: process.env.MAPBOX_API_TOKEN
      mapOptions: {
        hash: true
      }
    }, [
      h ErrorBoundary, [
        h SampleOverlay
      ]
    ]
  ]

export {MapPage}
