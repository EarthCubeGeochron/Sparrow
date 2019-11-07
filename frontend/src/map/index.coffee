import {Menu, MenuItem} from '@blueprintjs/core'
import {hyperStyled, classed} from '@macrostrat/hyper'
import styles from './module.styl'
import {SiteTitle} from 'app/components/navbar'
import {CatalogNavLinks} from '../admin'
import {AuthStatus} from 'app/auth'

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
  h MapNavbar, [
    h CatalogNavLinks
    h Menu.Divider
    h AuthStatus, {large: false}
  ]

export {MapPage}
