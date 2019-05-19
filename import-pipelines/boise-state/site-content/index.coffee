import {Markdown} from '@macrostrat/ui-components'
import aboutText from './about-the-lab.md'
import h from 'react-hyperscript'
import {LeafletMap} from 'plugins/leaflet-map'

export default {
  landingText: h Markdown, {src: aboutText}
  siteTitle: 'Boise State IGL'
  landingGraphic: h LeafletMap, {accessToken: process.env.MAPBOX_API_KEY}
}
