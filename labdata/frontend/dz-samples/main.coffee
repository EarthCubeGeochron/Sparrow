import {Component} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import { scaleLinear } from '@vx/scale'
import { AreaClosed } from '@vx/shape'
import { AxisLeft, AxisBottom } from '@vx/axis'
import { extent, min, max, histogram } from 'd3-array'
import gradients from './gradients'
import {kernelDensityEstimator, kernelEpanechnikov} from './kernel-density'

class DetritalZirconComponent extends Component
  constructor: ->
    super arguments...
    @state = {data: null}
    @getData()

  render: ->
    {data} = @state
    return null unless data?


    accessor = (d)-> d.best_age
    minMax = data.map (d)->
      [min(d.grain_data, accessor),
       min(d.grain_data, accessor)]

    __ = [
      min(minMax, (d)->d[0])
      max(minMax, (d)->d[1])
    ]

    hist = histogram()
      .domain([0,4000])
      .thresholds(80)
      .value (d)->d.best_age

    width = 900
    height = 500
    xScale = scaleLinear({
      range: [0, width]
      domain: [0,4000]
    })

    yScale = scaleLinear({
      range: [height, 0]
      domain: [0, 0.04]
    })


    h 'svg', { width, height }, data.map (sampleData, i)->
      {grain_data} = sampleData

      xTicks = xScale.ticks(400)
      kde = kernelDensityEstimator(kernelEpanechnikov(30), xTicks)
      fn = (d)->d.best_age
      kdeData = kde(grain_data.map(fn))
      console.log kdeData

      id = "gradient_#{i}"
      h 'g', [
        h gradients[i], {id}
        h AreaClosed, {
          data: kdeData
          yScale
          x: (d)-> xScale(d[0])
          y: (d)-> yScale(d[1])
          fill: "url(##{id})"
          transform: "translate(0,#{-i*50})"
        }
      ]


  getData: ->
    {data} = await get '/api/v1/dz_sample'
    @setState {data}

export {DetritalZirconComponent}
