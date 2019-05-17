import {Markdown} from '@macrostrat/ui-components'
import aboutText from './about.md'
import h from 'react-hyperscript'

export default {
  landingText: h Markdown, {src: aboutText}
  siteTitle: 'Arizona LaserChron Center'
}
