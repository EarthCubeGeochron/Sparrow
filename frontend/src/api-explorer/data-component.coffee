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

Bold = styled.span"""font-weight:600;"""

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
      a = "#{a}"
      if a == 'false'
        a = h Bold, null, 'F'
      if a == 'true'
        a = h Bold, null, 'T'
      if a == 'null'
        a = '—'

      h Cell, null, a

    sizes = []
    for k,v of data[0]
      columns.push h Column, {key: k, name: k, cellRenderer: cellRenderer(k)}
      if typeof v is 'boolean'
        sz = 50
      else
        sz = 100
      sizes.push sz

    h Table, {
      numRows: data.length
      defaultRowHeight: 30
      columnWidths: sizes
      className
    }, columns

DataTable = styled(DataTable__)"""
  margin: 1em 0 2em 0;
  font-size: 1.2em;
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
