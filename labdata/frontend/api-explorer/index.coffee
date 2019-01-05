import 'babel-polyfill'
import React from "react"
import {render} from 'react-dom'
import { BrowserRouter as Router, Route, Link } from "react-router-dom"
import h from 'react-hyperscript'
import {RouteComponent} from './route-component'

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
