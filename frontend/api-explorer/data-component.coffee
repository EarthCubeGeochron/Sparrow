import {Component} from 'react'
import h from 'react-hyperscript'
import styled from '@emotion/styled'
import {JSONToggle} from './utils'
import {get} from 'axios'
import {JSONCollapsePanel} from './collapse-panel'
import { PagedAPIView } from "@macrostrat/ui-components"
import { Cell, Column, Table } from "@blueprintjs/table"
import ReactJson from 'react-json-view'

import "@blueprintjs/table/lib/css/table.css"

class DataTable__ extends Component
  render: ->
    {data, className} = @props
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
      className
    }, columns

DataTable = styled(DataTable__)"""
  margin: 1em 0 2em 0;
"""

class APIDataComponentInner extends JSONCollapsePanel
  constructor: (props)->
    super props
    @state = {showJSON: false}

  renderDataInterior: (data)=>
    {showJSON} = @state
    if showJSON
      return h ReactJson, {src: data}
    h DataTable, {data}

  renderInterior: ->
    {route, params} = @props
    console.log params
    return null unless route?

    h PagedAPIView, {
      topPagination: true,
      bottomPagination: false,
      route,
      params,
      perPage: 20
    }, @renderDataInterior

APIDataComponent = (props)->
  h APIDataComponentInner, {
    storageID: 'data'
    className: 'data'
    title: 'Data'
    props...
  }

export {APIDataComponent}
