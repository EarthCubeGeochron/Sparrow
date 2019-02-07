import h from 'react-hyperscript'
import {Tag} from '@blueprintjs/core'

Parameter = (props)->
  {name, type, default: defaultArg, description} = props

  if type == 'boolean'
    type = 'bool'

  attrs = [
    h Tag, type
  ]

  if description? and description.startsWith("Column")
    description = null
    attrs.push h Tag, "column"

  if defaultArg?
    attrs.push h Tag, "default: #{defaultArg}"


  h 'div.argument.bp3-card.bp3-interactive', {key: name}, [
    h 'h5.name', name
    h 'div.attributes', attrs
    h('p.description', description) if description?
  ]

export {Parameter}
