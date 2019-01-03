import React from "react"
import {render} from 'react-dom'
import { BrowserRouter as Router, Route, Link } from "react-router-dom"
import h from 'react-hyperscript'

Homepage = ->
  h 'div', [
    h 'h1', 'Lab Data Interface – API Explorer'
  ]

AppRouter = ->
  h Router, [
    h 'div', [
      h Route, {path: '/', component: Homepage}
    ]
  ]

el = document.querySelector("#container")
render(h(AppRouter), el)
