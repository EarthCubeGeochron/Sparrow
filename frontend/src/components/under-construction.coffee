import {NonIdealState} from '@blueprintjs/core'
import h from 'react-hyperscript'

UnderConstruction = (props)->
  {name} = props
  rest =" view is not yet implemented. Sorry!"
  desc = "This"+rest
  if name?
    desc = h [
      "The "
      h 'b', name
      rest
    ]
  h NonIdealState, {
    title: "Under construction"
    description: desc
    icon: 'build'
  }

export {UnderConstruction}
