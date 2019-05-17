import {Component, createElement} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import {APIResultView} from '@macrostrat/ui-components'
import { scaleLinear } from '@vx/scale'
import { AreaClosed } from '@vx/shape'
import { AxisLeft, AxisBottom } from '@vx/axis'
import { extent, min, max, histogram } from 'd3-array'
import gradients from './gradients'
import {kernelDensityEstimator, kernelEpanechnikov, kernelGaussian} from './kernel-density'

import './main.styl'

class DetritalZirconBase extends Component
  render: ->
    {data, session_id} = @props
    return null unless data?

    accessor = (d)-> d.value

    minmax = extent data, accessor
    minmax = [minmax[0] - 5, minmax[1] + 5]

    hist = histogram()
      .domain(minmax)
      .thresholds(80)
      .value accessor

    margin = 10
    marginTop = 10
    marginBottom = 50
    innerWidth = 750
    eachHeight = 150
    height = eachHeight+marginTop+marginBottom
    width = innerWidth+2*margin

    xScale = scaleLinear({
      range: [0, width]
      domain: minmax
    })
    delta = minmax[1]-minmax[0]
    bandwidth = delta/50

    label = "Age (Ma)"
    tickFormat = (d)->d
    if delta > 1000
      label = "Age (Ga)"
      tickFormat = (d)->d/1000


    xTicks = xScale.ticks(400)
    kde = kernelDensityEstimator(kernelGaussian(bandwidth), xTicks)
    kdeData = kde(data.map(accessor))

    # All KDEs should have same height
    maxProbability = max kdeData, (d)->d[1]

    yScale = scaleLinear({
      range: [eachHeight, 0]
      domain: [0, maxProbability]
    })

    labelProps = {label}

    id = "gradient_1"

    h 'svg', { width, height}, [
      h 'g', {
        transform: "translate(#{margin},#{marginTop})"
      }, [
        h gradients[0], {id}
        createElement 'foreignObject', {x: 0, y: -20, width: 500, height: 50}, (
          h 'h4', null, [
            "#{data.length} grains"
          ]
        )
        h AreaClosed, {
          data: kdeData
          yScale
          x: (d)-> xScale(d[0])
          y: (d)-> yScale(d[1])
          fill: "url(##{id})"
        }
        h AxisBottom, {
          scale: xScale
          numTicks: 10
          tickLength: 4
          tickFormat
          strokeWidth: 1.5
          top: eachHeight
          labelProps...
        }
      ]
    ]

DetritalZirconComponent = (props)->
  route = '/datum'
  h APIResultView, {
    route,
    params: {unit: 'Ma', is_accepted: true, props...}
  }, (data)->
    h DetritalZirconBase, {data, props...}

export {DetritalZirconComponent}
