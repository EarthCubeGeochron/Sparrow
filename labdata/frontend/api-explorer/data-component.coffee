import {Component} from 'react'
import h from 'react-hyperscript'
import {JSONCollapsePanel} from './collapse-panel'
import {get} from 'axios'
import { APIResultView, APIConsumer } from "@macrostrat/ui-components"
import { Cell, Column, Table } from "@blueprintjs/table"
import "@blueprintjs/table/lib/css/table.css"

class DataTable extends Component
  render: ->
    {data} = @props
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


class APIDataComponent extends Component
  @defaultProps: {route: null}
  render: ->
    {route, params} = @props
    return null unless route?
    h APIResultView, {route, params}, (data)=>
      h JSONCollapsePanel, {
        data
        storageID: 'data'
        className: 'data'
        title: 'Data'
      }, (
        h DataTable, {data}
      )

export {APIDataComponent}
