import React from "react"
import {render} from 'react-dom'
import { BrowserRouter as Router, Route, Link, Redirect } from "react-router-dom"
import h from 'react-hyperscript'

import {SiteTitle} from '../shared/util'
import {RouteComponent} from './route-component'

import '../shared/ui-init.styl'
import './main.styl'

AppRouter = ->
  h Router, {basename: '/api-explorer'}, [
    h 'div', [
      h SiteTitle, {subPage: 'API Explorer'}
      h 'div#api', [
        h Route, {
          path: '/',
          exact: true,
          render: -> h Redirect, {to: '/v1'}
        }
        h Route, {path: '/v1', component: RouteComponent}
      ]
    ]
  ]

el = document.querySelector("#container")
render(h(AppRouter), el)
