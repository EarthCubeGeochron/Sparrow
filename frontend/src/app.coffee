import h from 'react-hyperscript'
import {Component} from 'react'
import {join} from 'path'
import { BrowserRouter as Router, Route, Switch} from "react-router-dom"
import {HomePage} from './homepage'

import siteContent from 'site-content'
import {FrameProvider} from './frame'
import {Intent} from '@blueprintjs/core'
import {APIProvider} from '@macrostrat/ui-components'
import {APIExplorer} from './api-explorer'
import {Admin} from './admin'
import {AuthProvider} from './auth'
import {AppToaster} from './toaster'
import {PageFooter} from './shared/footer'

class AppMain extends Component
  render: ->
    {baseURL} = @props
    h Router, {basename: baseURL}, (
      h 'div.app', [
        h Switch, [
          h Route, {
            path: '/',
            exact: true,
            render: -> h HomePage
          }
          h Route, {path: '/admin', component: Admin}
          h Route, {path: '/api-explorer', component: APIExplorer}
        ]
        h PageFooter
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
