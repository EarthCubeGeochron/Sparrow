import aboutText from './index.md'
import {Markdown} from '@macrostrat/ui-components'
import h from 'react-hyperscript'
import {StepHeatingChart} from 'plugins/step-heating'
import {PlateauAgesComponent} from 'plugins/plateau-ages'
import {GLMap} from 'plugins/gl-map'

export default {
  siteTitle: "WiscAr"
  landingText: h Markdown, {src: aboutText}
  sessionDetail: (props)=>
    h StepHeatingChart, props
  adminBase: h(PlateauAgesComponent)
  landingGraphic: h GLMap, {accessToken: process.env.MAPBOX_API_TOKEN}
}
