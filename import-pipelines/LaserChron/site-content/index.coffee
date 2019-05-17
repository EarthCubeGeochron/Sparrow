import {Markdown} from '@macrostrat/ui-components'
import aboutText from './about.md'
import h from 'react-hyperscript'
import {DetritalZirconComponent} from 'plugins/dz-spectrum'
import {AggregateHistogram} from 'plugins/dz-aggregate-histogram'

export default {
  landingText: h Markdown, {src: aboutText}
  landingGraphic: h AggregateHistogram
  siteTitle: 'Arizona LaserChron Center'
  sessionDetail: (props)=>
    h DetritalZirconComponent, props
}
