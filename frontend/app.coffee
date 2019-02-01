import h from 'react-hyperscript'
import { BrowserRouter as Router, Route, Switch} from "react-router-dom"
import {HomePage} from './homepage'
import {APIExplorer} from './api-explorer'
import {ProjectPage} from './admin'
import {LoginPage, AuthStatus} from './auth'

App = ->
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
        h Route, {path: '/login', component: LoginPage}
      ]
    ]
  )

export {App}
