import ix from 'site-content/index.md'
import h from 'react-hyperscript'
import {SiteTitle, SiteNav} from './shared/util'

HomePage = ->
  h 'div', [
    h SiteTitle
    h SiteNav
    h 'div.bp3-running-text.bp3-text-large', {
      dangerouslySetInnerHTML: {__html: ix}
    }
  ]

export {HomePage}
