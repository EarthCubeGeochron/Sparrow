import {Component} from 'react'
import h from 'react-hyperscript'
import {JSONCollapsePanel} from './collapse-panel'
import {get} from 'axios'
import { Cell, Column, Table } from "@blueprintjs/table"
import "@blueprintjs/table/lib/css/table.css"

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

  renderDataTable: ->
    {data} = @state
    return null if not data?

    columns = []
    cellRenderer = (column)->(rowIndex)->
      a = data[rowIndex][column]
      # Special case for JSON rows
      if typeof a is "object"
        a = JSON.stringify a
      h Cell, null, "#{a}"

    for k,v of data[0]
      columns.push h Column, {key: k, name: k, cellRenderer: cellRenderer(k)}

    h Table, {
      numRows: data.length
      defaultRowHeight: 30
    }, columns

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
    }, @renderDataTable()

export {APIDataComponent}
