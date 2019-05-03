import h from 'react-hyperscript'
import {join} from 'path'
import { BrowserRouter as Router, Route, Switch} from "react-router-dom"
import {HomePage} from './homepage'

import {Intent} from '@blueprintjs/core'
import {APIProvider} from '@macrostrat/ui-components'
import {APIExplorer} from './api-explorer'
import {Admin} from './admin'
import {AuthProvider} from './auth'
import {AppToaster} from './toaster'

AppMain = ({baseURL})->
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
    ]
  )

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

  h APIProvider, {baseURL: apiBaseURL, onError: errorHandler}, (
    h AuthProvider, null, (
      h AppMain, {baseURL}
    )
  )

export {App}
