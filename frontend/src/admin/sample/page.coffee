import hyper from '@macrostrat/hyper'
import styles from './module.styl'
import {UnderConstruction} from 'app/components'
import {GeoDeepDiveCard} from './gdd-card'
import {APIResultView} from '@macrostrat/ui-components'

h = hyper.styled(styles)

SamplePage = (props)->
  {match} = props
  {id} = match.params
  h APIResultView, {route: "/sample", params: {id}}, (data)=>
    d = data[0]
    return null unless d?
    h 'div.sample', [
      h 'h2', "Sample #{d.name}"
      h 'h3', "Metadata helpers"
      h GeoDeepDiveCard, {sample_name: d.name}
    ]

export {SamplePage}
