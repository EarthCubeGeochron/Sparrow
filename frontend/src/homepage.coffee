import h from 'react-hyperscript'
import {AppNavbar, NavButton} from 'app/shared/navbar'
import {SampleMap} from './map'
import {Frame} from './frame'
import {InsetText} from 'app/layout'

HomePage = ->
  h 'div.homepage', [
    h InsetText, null, [
      h Frame, {id: "landingText"}, "Landing page text goes here."
      h Frame, {id: "landingGraphic"}, (
        h SampleMap
      )
    ]
  ]

export {HomePage}
