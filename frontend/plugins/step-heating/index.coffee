import {render} from 'react-dom'
import {Component} from 'react'
import h from 'react-hyperscript'
import styled from '@emotion/styled'
import { scaleLinear } from '@vx/scale'
import { AreaClosed } from '@vx/shape'
import { AxisLeft, AxisBottom } from '@vx/axis'
import { APIResultView } from '@macrostrat/ui-components'
import { min, max } from 'd3-array'
import T from 'prop-types'

d = styled.div"""
min-height: 200px;
width: 10%;
background: purple;
margin-bottom: 1em;
"""

errorExtent = (arr)->
  mn = min arr, (d)-> d.value - d.error
  mx = max arr, (d)-> d.value + d.error
  [mn, mx]

class StepHeatingChart extends Component
  constructor: (props)->
    super props

  renderChart: (data)=>
    width = 800
    height = 450

    margin = 50
    innerWidth = width-2*margin
    innerHeight = height-2*margin

    heatingSteps = data.filter (d)-> d.session_index?
    heatingSteps.sort (a,b)-> b.session_index-a.session_index

    interpretedAges = data.filter (d)-> not d.session_index?

    ages = heatingSteps.map (d)-> {
        in_plateau: not d.is_bad
        age: d.data.find (v)->v.parameter == 'step_age'
      }

    yExtent = errorExtent ages.map (d)->d.age

    xScale = scaleLinear({
      range: [0, innerWidth]
      domain: [0, heatingSteps.length]
    })

    yScale = scaleLinear({
      range: [innerHeight, 0]
      domain: yExtent
    })

    deltaX = xScale(1)-xScale(0)

    h 'svg.step-heating-chart', {
      width: 900, height
    }, [
      h 'g.chart-main', {
        transform: "translate(#{margin},#{margin})"
      }, [
        h 'g.data-area', [
          h 'g.heating-steps', ages.map (d,i)->
            {age, in_plateau} = d
            mn = age.value-age.error
            mx = age.value+age.error
            y = yScale(mx)

            h 'rect', {
              x: xScale(i),
              y,
              width: deltaX,
              height: yScale(mn)-y
              fill: if in_plateau then "#888" else "#aaa"
            }
        ]
        h AxisBottom, {
          scale: xScale
          numTicks: 10
          top: innerHeight
        }
        h AxisLeft, {
          scale: yScale
          numTicks: 10
        }
      ]
    ]

  render: ->
    {session_id} = @props
    console.log session_id
    h APIResultView, {
      route: "/analysis"
      params: {session_id}
    }, @renderChart


export {StepHeatingChart}
