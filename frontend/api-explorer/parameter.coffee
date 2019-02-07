import h from 'react-hyperscript'
import {Tag} from '@blueprintjs/core'

Parameter = (props)->
  {name, type, default: defaultArg, description} = props
  h 'div.argument.bp3-card.bp3-interactive', {key: name}, [
    h 'h5.name', name
    h 'div.attributes', [
      h Tag, type
    ]
    h('p.description', description) if description?
    h('p.default', "Default: #{defaultArg}") if defaultArg?
  ]

export {Parameter}
