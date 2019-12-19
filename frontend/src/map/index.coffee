import {useEffect, useState} from 'react'
import {Menu, MenuItem, Popover} from '@blueprintjs/core'
import {hyperStyled, classed} from '@macrostrat/hyper'
import styles from './module.styl'
import {SiteTitle} from 'app/components/navbar'
import {CatalogNavLinks} from '../admin'
import {AuthStatus} from 'app/auth'
import {MapPanel} from './map-area'
import {HashLink} from 'react-router-hash-link'

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
    }
  ]

MapLink = (props)->
  {zoom, latitude, longitude, children, rest...} = props
  h HashLink, {to: "/map##{zoom}/#{latitude}/#{longitude}", rest...}, children

export {MapPage, MapLink}
