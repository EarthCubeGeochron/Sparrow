import h from 'react-hyperscript'
import { BrowserRouter as Router, Route } from "react-router-dom"
import {HomePage} from './homepage'
import {APIExplorer} from './api-explorer'

App = ->
  h Router, {basename: '/'}, (
    h 'div.app', [
      h Route, {
        path: '/',
        exact: true,
        render: -> h HomePage
      }
      h Route, {path: '/api-explorer', component: APIExplorer}
    ]
  )

export {App}
