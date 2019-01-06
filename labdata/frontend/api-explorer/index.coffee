import 'babel-polyfill'
import React from "react"
import {render} from 'react-dom'
import { BrowserRouter as Router, Route, Link } from "react-router-dom"
import h from 'react-hyperscript'

import {RouteComponent} from './route-component'

# Should import this in styles
import '@blueprintjs/core/lib/css/blueprint.css'
import '@blueprintjs/icons/lib/css/blueprint-icons.css'
import './main.styl'

AppRouter = ->
  h Router, {basename: '/api-explorer'}, [
    h 'div', [
      h 'h1', 'Lab Data Interface – API Explorer'
      h 'div#api', [
        h Route, {path: '/', component: RouteComponent}
      ]
    ]
  ]

el = document.querySelector("#container")
render(h(AppRouter), el)
