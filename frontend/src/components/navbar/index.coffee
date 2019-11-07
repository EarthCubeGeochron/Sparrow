import {hyperStyled, classed} from '@macrostrat/hyper'
import {Navbar, Button, ButtonGroup, Icon, Menu, MenuItem} from '@blueprintjs/core'
import {NavLink, Route, Switch} from 'react-router-dom'
import styled from "@emotion/styled"
import {LinkButton, NavLinkButton} from '@macrostrat/ui-components'

import {AuthStatus} from 'app/auth'
import {Frame} from 'app/frame'
import styles from './module.styl'

h = hyperStyled(styles)

NavButton = classed(NavLinkButton, 'navbar-button')
MainNavbar = classed(Navbar, "main-navbar")

SiteTitle = ->
  h NavLink, {to: '/'}, (
    h Frame, {id: 'siteTitle'}, "Test Lab"
  )


Nav = ({children, fullTitle, subtitle, rest...})->
  children ?= null
  h MainNavbar, {rest...}, [
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

AppNavbar = styled(Nav)"""
  border-radius: 5px
"""

AppNavbar.Divider = Navbar.Divider

export {AppNavbar, NavButton, SiteTitle}
