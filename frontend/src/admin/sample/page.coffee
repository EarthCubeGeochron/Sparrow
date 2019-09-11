import hyper from '@macrostrat/hyper'
import styles from './module.styl'
import {UnderConstruction} from 'app/components'

h = hyper.styled(styles)

SamplePage = (props)->
  {match} = props
  h UnderConstruction, {name: "Sample Page"}

export {SamplePage}
