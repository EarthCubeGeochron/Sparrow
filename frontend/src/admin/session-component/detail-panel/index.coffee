import hyper from '@macrostrat/hyper'
import styles from './module.styl'
import {Component} from 'react'
import {Card, Breadcrumbs} from '@blueprintjs/core'
import {APIResultView} from '@macrostrat/ui-components'
import ReactJson from 'react-json-view'
import {format} from 'd3-format'
import {group} from 'd3-array'

fmt = format(".3g")

h = hyper.styled(styles)

toTitleCase = (str)->
  func = (txt)->txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  str.replace(/\w\S*/g, func)

Material = (props)->
  {data} = props
  return null unless data?
  items = data.reverse().map (d, i)->{text: h('div',d), current: i == 0}
  h 'div.material.datum', [
    h 'h4', "Material"
    h Breadcrumbs, {items}
  ]


AnalysisAttributes = (props)->
  {analysis_id} = props
  h APIResultView, {route: "/attribute", params: {analysis_id}, placeholder: null }, (data)=>
    return null unless data?
    return null if data.length == 0
    groupedData = group data, (d)->d.parameter

    h Array.from groupedData, ([k,v])->
      h "li.attribute", [
        h 'span.parameter', "#{k}:"
        h 'ul.values', v.map (d)->
          h 'li.value', d.value
      ]

Unit = ({unit})->
  if ['unknown','ratio'].includes(unit)
    return null
  h 'span.unit', unit

Datum = (props)->
  {value: d} = props
  h 'li.datum.bp3-text', [
    h 'span.parameter', "#{d.parameter}:"
    " "
    h 'span.value', fmt(d.value)
    h.if(d.error?) 'span.error', [
      "±"
      h 'span.error-value', fmt(d.error)
      h.if(d.error_metric?) 'span.error-metric', (
        "(#{d.error_metric})"
      )
    ]
    " "
    h Unit, {unit: d.unit}
  ]

DataCollection = ({data, analysis_id})->
  datumList = h data.map (d)->
    h Datum, {value: d}

  h 'ul.data', [
    datumList,
    h AnalysisAttributes, {analysis_id}
  ]


AnalysisDetails = (props)->
  {data: a} = props
  {analysis_id} = a

  h Card, {className: 'analysis-details'}, [
    h.if(a.analysis_type?) 'h3.analysis-type', toTitleCase(a.analysis_type)
    h Material, {data: a.material}
    h 'div.main', [
      h 'div.data', [
        h 'h4', "Data"
        h DataCollection, {data: a.data, analysis_id}
      ]
    ]
  ]

SessionDetails = (props)->
  {data, showTitle} = props
  showTitle ?= false
  h 'div.session-details', [
    h.if(showTitle) 'h2', "Analysis details"
    data.map (d)->
      h AnalysisDetails, {data: d}
  ]

SessionDetailPanel = (props)->
  {session_id} = props
  h APIResultView, {
    route: "/analysis"
    params: {session_id}
  }, (data)=>
    h SessionDetails, {data: data}

export {SessionDetailPanel}
