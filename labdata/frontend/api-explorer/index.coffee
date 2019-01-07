import 'babel-polyfill'
import React from "react"
import {render} from 'react-dom'
import { BrowserRouter as Router, Route, Link, Redirect } from "react-router-dom"
import h from 'react-hyperscript'
import { FocusStyleManager } from "@blueprintjs/core"

import {RouteComponent} from './route-component'

# Should import this in styles
import '@blueprintjs/core/lib/css/blueprint.css'
import '@blueprintjs/icons/lib/css/blueprint-icons.css'
import './main.styl'

FocusStyleManager.onlyShowFocusOnTabs()

AppRouter = ->
  h Router, {basename: '/api-explorer'}, [
    h 'div', [
      h 'h1', 'Lab Data Interface – API Explorer'
      h 'div#api', [
        h Route, {path: '/', exact: true, render: => h Redirect, {to: '/v1'}}
        h Route, {path: '/v1', component: RouteComponent}
      ]
    ]
  ]

el = document.querySelector("#container")
render(h(AppRouter), el)
