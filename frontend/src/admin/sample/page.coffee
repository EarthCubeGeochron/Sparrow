import hyper from '@macrostrat/hyper'
import styles from './module.styl'

h = hyper.styled(styles)

SamplePage = ->
  {match} = @props
  console.log match
  h 'div'

export {SamplePage}
