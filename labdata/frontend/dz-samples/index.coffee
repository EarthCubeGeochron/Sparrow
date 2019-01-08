import {render} from 'react-dom'
import h from 'react-hyperscript'

import '../shared/ui-init'
import {SiteTitle} from '../shared/util'

MainPage = ->
  h 'div', [
    h SiteTitle, {subPage: 'Detrital zircon samples'}
  ]

el = document.querySelector("#container")
render(h(MainPage), el)
