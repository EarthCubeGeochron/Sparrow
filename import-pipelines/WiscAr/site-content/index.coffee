import aboutText from './index.md'
import {Markdown} from '@macrostrat/ui-components'
import h from 'react-hyperscript'
import {StepHeatingChart} from 'plugins/step-heating'
import {PlateauAgesComponent} from 'plugins/plateau-ages'

export default {
  siteTitle: "WiscAr"
  landingText: h Markdown, {src: aboutText}
  sessionDetail: (props)=>
    h StepHeatingChart, props
  adminBase: h(PlateauAgesComponent)
}
