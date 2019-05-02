import ix from 'site-content/index.md'
import h from 'react-hyperscript'
import {AppNavbar, NavButton} from 'app/shared/navbar'
import {SampleMap} from './map'

HomePage = ->
  h 'div', [
    h AppNavbar, {fullTitle: true}, [
      h NavButton, {to: '/admin'}, "Admin"
      h NavButton, {to: '/api-explorer/v1'}, "API Explorer"
    ]
    h 'div.bp3-running-text.bp3-text-large', {
      dangerouslySetInnerHTML: {__html: ix}
    }
    h SampleMap
  ]

export {HomePage}
