import '../shared/ui-init'

import React from "react"
import {render} from 'react-dom'
import { Route, Link, Redirect } from "react-router-dom"
import h from 'react-hyperscript'

import {AppNavbar} from 'app/shared/navbar'
import {RouteComponent} from './route-component'

import './main.styl'

APIExplorer = (props)->
  {match} = props
  h 'div', [
    h AppNavbar, {subtitle: 'API Explorer', fullTitle: true}
    h 'div#api', [
      h Route, {
        path: "#{match.url}",
        exact: true,
        render: -> h Redirect, {to: "#{match.url}/v1"}
      }
      h Route, {path: "#{match.url}/v1", component: RouteComponent}
    ]
  ]

export {APIExplorer}
