import h from 'react-hyperscript'
import {Component} from 'react'

class SessionComponent extends Component
  render: ->
    {id} = @props
    h 'div.session', [
      h 'code.session-id'
    ]

export {SessionComponent}
