import h from 'react-hyperscript'
import {Component} from 'react'
import {join} from 'path'
import { BrowserRouter as Router, Route, Switch, useLocation} from "react-router-dom"
import {HomePage} from './homepage'

import siteContent from 'site-content'
import {FrameProvider} from './frame'
import {Intent} from '@blueprintjs/core'
import {APIProvider} from '@macrostrat/ui-components'
import {APIExplorer} from './api-explorer'
import {PageFooter} from './shared/footer'
import {AuthProvider} from './auth'
import {AppToaster} from './toaster'
import {Catalog, CatalogNavLinks} from './admin'
import {AppNavbar, NavButton} from './components/navbar'
import {MapPage} from './map'
import styled from '@emotion/styled'

AppHolder = styled.div"""
display: flex;
flex-direction: column;
min-height: 100vh;
"""

Expander = styled.div"""
flex-grow: 1;
"""

GlobalUI = (props)->
  ###
  Defines a hideable global UI component
  ###
  location = useLocation()
  hidePaths = ['/map']
  return null if hidePaths.includes(location.pathname)
  h [
    props.children
  ]

MainNavbar = (props)->
  h AppNavbar, {fullTitle: true}, [
    h CatalogNavLinks, {base: '/catalog'}
    h NavButton, {to: '/map'}, "Map"
    h AppNavbar.Divider
    h NavButton, {to: '/api-explorer/v1'}, "API"
  ]

class AppMain extends Component
  render: ->
    {baseURL} = @props
    h Router, {basename: baseURL}, (
      h AppHolder, [
        h Expander, [
          h GlobalUI, null, (
            h MainNavbar
          )
          h Switch, [
            h Route, {
              path: '/',
              exact: true,
              render: -> h HomePage
            }
            h Route, {
              path: '/catalog',
              render: -> h Catalog, {base: '/catalog'}
            }
            h Route, {
              path: '/map'
              component: MapPage
            }
            h Route, {path: '/api-explorer', component: APIExplorer}
          ]
        ]
        h GlobalUI, null, (
          h PageFooter
        )
      ]
    )
  componentDidMount: ->
    labname = process.env.SPARROW_LAB_NAME
    document.title = if labname? then "#{labname} – Sparrow" else "Sparrow"

errorHandler = (route, response)->
  {error} = response
  if error?
    msg = error.message
  message = h 'div.api-error', [
    h 'code.bp3-code', route
    h 'p', msg
  ]
  AppToaster.show {message, intent: Intent.DANGER}

App = ->
  baseURL = process.env.BASE_URL or "/"
  apiBaseURL = join(baseURL,'/api/v1')
  console.log apiBaseURL

  h FrameProvider, {overrides: siteContent}, (
    h APIProvider, {baseURL: apiBaseURL, onError: errorHandler}, (
      h AuthProvider, null, (
        h AppMain, {baseURL}
      )
    )
  )

export {App}
