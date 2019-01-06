import {Component} from 'react'
import h from 'react-hyperscript'
import {CollapsePanel} from './collapse-panel'

class APIDataComponent extends Component
  @defaultProps: {data: null}
  constructor: (props)->
    super props

  render: ->
    {data} = @props
    h CollapsePanel, {className: 'data', title: 'Data'}, [
      h 'div', 'Data'
    ]

export {APIDataComponent}
