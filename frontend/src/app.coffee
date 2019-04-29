import h from 'react-hyperscript'
import { BrowserRouter as Router, Route, Switch} from "react-router-dom"
import {HomePage} from './homepage'

import {Intent} from '@blueprintjs/core'
import {APIProvider} from '@macrostrat/ui-components'
import {APIExplorer} from './api-explorer'
import {ProjectPage} from './admin'
import {AuthProvider} from './auth'
import {AppToaster} from './toaster'

AppMain = ->
  h Router, {basename: '/labs/wiscar'}, (
    h 'div.app', [
      h Switch, [
        h Route, {
          path: '/',
          exact: true,
          render: -> h HomePage
        }
        h Route, {path: '/admin', component: ProjectPage}
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
  h APIProvider, {baseURL: '/labs/wiscar/api/v1', onError: errorHandler}, (
    h AuthProvider, null, (
      h AppMain
    )
  )

export {App}
