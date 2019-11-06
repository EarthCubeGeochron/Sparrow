import h from '@macrostrat/hyper'
import {Navbar, Button, ButtonGroup, Icon} from '@blueprintjs/core'
import {NavLink, Route, Switch} from 'react-router-dom'
import {AuthStatus} from 'app/auth'
import styled from "@emotion/styled"
import {LinkButton, NavLinkButton} from '@macrostrat/ui-components'
import {Frame} from '../frame'

NavButton_ = (props)->
  h NavLinkButton, {props...}

NavButton = styled(NavButton_)"""
margin-right: 1em;
&.active {
  background-color: #d8e1e8;
}
"""

Nav = ({children, fullTitle, subtitle, rest...})->
  children ?= null
  divider = null
  if children?
    divider = h Navbar.Divider
  vals = [
    h NavLink, {to: '/'}, (
      h Frame, {id: 'siteTitle'}, "Test Lab"
    )
  ]
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

AppNavbar.Divider = Navbar.Divider

MapNavbar = ->
  h 'div'

export {AppNavbar, MapNavbar, NavButton}
