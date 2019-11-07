import h from 'react-hyperscript'
import {AppNavbar, NavButton} from 'app/components/navbar'
import {SampleMap} from '../plugins/globe'
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
