import hyper from '@macrostrat/hyper'
import {APIResultView} from '@macrostrat/ui-components'

import {SampleContextMap} from 'app/components'
import {GeoDeepDiveCard} from './gdd-card'
import styles from './module.styl'
h = hyper.styled(styles)

Parameter = ({key, value, rest...})->
  h 'div.parameter', rest, [
    h 'span.key', key
    h 'span.value', value
  ]


ProjectInfo = ({sample: d})->
  if not d.project_name
    return h 'em', "No project"
  h Parameter, {
    className: 'project'
    key: 'Project'
    value: d.project_name
  }

LocationBlock = (props)->
  {sample} = props
  {geometry} = sample
  return null unless geometry?
  h SampleContextMap, {
    center: geometry.coordinates
    zoom: 8
  }


SamplePage = (props)->
  {match} = props
  {id} = match.params
  h APIResultView, {route: "/sample", params: {id}}, (data)=>
    d = data[0]
    return null unless d?
    h 'div.sample', [
      h 'h2', "Sample #{d.name}"
      h 'div.basic-info', [
        h ProjectInfo, {sample: d}
      ]
      h LocationBlock, {sample: d}
      #h 'h3', "Metadata helpers"
      #h GeoDeepDiveCard, {sample_name: d.name}
    ]

export {SamplePage}
