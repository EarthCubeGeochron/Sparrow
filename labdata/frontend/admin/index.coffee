import {render} from 'react-dom'
import h from 'react-hyperscript'

import '../shared/ui-init'
import {SiteTitle} from '../shared/util'
import {ProjectListComponent} from './project-component'

MainPage = ->
  h 'div', [
    h SiteTitle, {subPage: 'Admin'}
    h ProjectListComponent
  ]

el = document.querySelector("#container")
render(h(MainPage), el)
