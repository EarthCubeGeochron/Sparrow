import {Markdown} from '@macrostrat/ui-components'
import aboutText from './about.md'
import h from 'react-hyperscript'

siteTitle = process.env.SPARROW_LAB_NAME or 'Fab Lab 🔬 🌈'

export default {
  landingText: h Markdown, {src: aboutText}
  siteTitle
}
