import {render} from 'react-dom'
import h from 'react-hyperscript'

import '../shared/ui-init'
import {SiteTitle} from '../shared/util'
import {ProjectComponent} from './project-component'

MainPage = ->
  h 'div', [
    h SiteTitle, {subPage: 'Admin'}
    h ProjectComponent
  ]

el = document.querySelector("#container")
render(h(MainPage), el)
