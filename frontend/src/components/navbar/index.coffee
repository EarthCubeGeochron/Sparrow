import {hyperStyled, classed, addClassNames} from '@macrostrat/hyper'
import {Navbar, Button, ButtonGroup, Icon, Menu, MenuItem} from '@blueprintjs/core'
import {NavLink, Route, Switch} from 'react-router-dom'
import {LinkButton, NavLinkButton} from '@macrostrat/ui-components'

import {AuthStatus} from 'app/auth'
import {Frame} from 'app/frame'
import styles from './module.styl'

h = hyperStyled(styles)

NavButton = classed(NavLinkButton, 'navbar-button')

SiteTitle = ->
  h NavLink, {to: '/'}, (
    h Frame, {id: 'siteTitle'}, "Test Lab"
  )

AppNavbar = ({children, fullTitle, subtitle, rest...})->
  children ?= null
  p = addClassNames(rest, 'app-navbar')
  h Navbar, p, [
    h Navbar.Group, [
      h Navbar.Heading, [
        h 'h1.site-title', null, [
          h SiteTitle
          h.if(subtitle?) [
            h 'span', ":"
            h 'span.subtitle', subtitle
          ]
        ]
      ]
      h.if(children?) Navbar.Divider
      children
      h AuthStatus, {className: 'auth-right'}
    ]
  ]

AppNavbar.Divider = Navbar.Divider


MinimalNavbar = (props)->
  h 'div.minimal-navbar', props

export {AppNavbar, NavButton, SiteTitle, MinimalNavbar}
