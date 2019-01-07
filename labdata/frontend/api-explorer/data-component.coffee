import {Component} from 'react'
import h from 'react-hyperscript'
import {JSONCollapsePanel} from './collapse-panel'
import {get} from 'axios'

class APIDataComponent extends Component
  @defaultProps: {route: null}
  constructor: (props)->
    super props
    @state = {data: null}
    @getData()

  getData: ->
    {route} = @props
    return unless route?
    {data} = await get route
    @setState {data}

  render: ->
    {route} = @props
    {data} = @state
    # Just as a shorthand, there will be no results unless
    # there are arguments for any given route
    return null unless route?
    h JSONCollapsePanel, {
      data
      storageID: 'data'
      className: 'data'
      title: 'Data'
    }, [
      h 'div', "Data"
    ]

export {APIDataComponent}
