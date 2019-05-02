import h from 'react-hyperscript'
import {Navbar, Button, ButtonGroup, Icon} from '@blueprintjs/core'
import {NavLink, Route, Switch} from 'react-router-dom'
import cfg from 'site-content/variables'
import {AuthStatus} from 'app/auth'
import styled from "@emotion/styled"
import {LinkButton} from '@macrostrat/ui-components'

NavButton_ = (props)->
  h LinkButton, {props..., minimal: true}

NavButton = styled(NavButton_)"""
margin-right: 1em;
"""

Nav = ({children, fullTitle, subtitle, rest...})->
  children ?= null
  divider = null
  if children?
    divider = h Navbar.Divider
  longInfo = null
  if fullTitle
    longInfo = h 'span', " Sparrow"
  vals = [
    h NavLink, {to: '/'}, "#{cfg.siteTitle}"
    longInfo
  ]
  console.log vals
  if subtitle?
    vals.push h 'span', ":"
    vals.push h 'span.subtitle', subtitle

  h Navbar, {rest...}, [
    h Navbar.Group, [
      h Navbar.Heading, [
        h 'h1.site-title', null, vals
      ]
      divider
      children
      h AuthStatus
    ]
  ]

AppNavbar = styled(Nav)"""
  border-radius: 5px
"""

export {AppNavbar, NavButton}
