import h from 'react-hyperscript'
import { BrowserRouter as Router, Route, Switch} from "react-router-dom"
import {HomePage} from './homepage'
import {APIProvider} from '@macrostrat/ui-components'
import {APIExplorer} from './api-explorer'
import {ProjectPage} from './admin'
import {AuthStatus, AuthProvider} from './auth'

AppMain = ->
  h Router, {basename: '/'}, (
    h 'div.app', [
      h AuthStatus
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

App = ->
  h APIProvider, {baseURL: '/api/v1'}, (
    h AuthProvider, null, (
      h AppMain
    )
  )

export {App}
