import hyper from '@macrostrat/hyper'
import styles from './module.styl'
import {Component} from 'react'
import {Card, Breadcrumbs} from '@blueprintjs/core'
import {APIResultView} from '@macrostrat/ui-components'
import ReactJson from 'react-json-view'
import {format} from 'd3-format'

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

Datum = (props)->
  {value: d} = props
  h 'li.datum.bp3-text', [
    h 'span.title', "#{d.parameter}:"
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
    h 'span.unit', d.unit
  ]

AnalysisDetails = (props)->
  {data: a} = props

  h Card, {className: 'analysis-details'}, [
    h 'div.id', a.id
    h.if(a.analysis_type?) 'h3.analysis-type', toTitleCase(a.analysis_type)
    h Material, {data: a.material}
    h 'h4', "Data"
    h 'ul.data', a.data.map (d)->
      h Datum, {value: d}
  ]

SessionDetails = (props)->
  {data} = props
  h 'div.session-details', [
    h 'h2', "Analysis details"
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
