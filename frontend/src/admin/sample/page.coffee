import hyper from '@macrostrat/hyper'
import {APIResultView, LinkCard} from '@macrostrat/ui-components'

import {SampleContextMap} from 'app/components'
import {GeoDeepDiveCard} from './gdd-card'
import styles from './module.styl'
h = hyper.styled(styles)

Parameter = ({name, value, rest...})->
  h 'div.parameter', rest, [
    h 'h4.subtitle', name
    h 'p.value', null, value
  ]

ProjectLink = ({project_name, project_id})->
  return h('em', 'None') unless project_name? and project_id?
  h LinkCard, {
    to: "/catalog/project/#{project_id}"
  }, project_name


ProjectInfo = ({sample: d})->
  h 'div.parameter', [
    h 'h4.subtitle', 'Project'
    h 'p.value', [
      h ProjectLink, d
    ]
  ]

LocationBlock = (props)->
  {sample} = props
  {geometry, location_name} = sample
  return null unless geometry?
  h 'div.location', [
    h SampleContextMap, {
      center: geometry.coordinates
      zoom: 8
    }
    h.if(location_name) 'h5.location-name', location_name
  ]

Material = (props)->
  {material} = props
  h Parameter, {
    name: 'Material',
    value: material or h('em', 'None')
  }

SamplePage = (props)->
  {match} = props
  {id} = match.params
  h APIResultView, {route: "/sample", params: {id}}, (data)=>
    d = data[0]
    {material} = d
    return null unless d?
    h 'div.sample', [
      h 'h3.page-type', 'Sample'
      h LocationBlock, {sample: d}
      h 'h2', d.name
      h 'div.basic-info', [
        h ProjectInfo, {sample: d}
        h Material, {material}
      ]
      h 'h3', "Metadata helpers"
      h GeoDeepDiveCard, {sample_name: d.name}
    ]

export {SamplePage}
