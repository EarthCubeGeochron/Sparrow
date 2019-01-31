import ix from 'site-content/index.md'
import h from 'react-hyperscript'
import {SiteTitle, SiteNav} from './shared/util'

HomePage = ->
  h 'div', [
    h SiteTitle
    h SiteNav
    h 'div', {dangerouslySetInnerHTML: {__html: ix}}
  ]

export {HomePage}
