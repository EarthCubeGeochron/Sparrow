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

    ageValues = heatingSteps.map (d)->
      d.data.find (v)->v.parameter == 'step_age'

    yExtent = errorExtent ageValues

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
          h 'g.heating-steps', ageValues.map (d,i)->
            console.log d
            mn = d.value-d.error
            mx = d.value+d.error
            y = yScale(mx)
            console.log y

            h 'rect', {
              x: xScale(i),
              y,
              width: deltaX,
              height: yScale(mn)-y
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
