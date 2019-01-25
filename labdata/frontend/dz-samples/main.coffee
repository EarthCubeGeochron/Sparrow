import {Component, createElement} from 'react'
import h from 'react-hyperscript'
import {get} from 'axios'
import {APIResultView} from '@macrostrat/ui-components'
import { scaleLinear } from '@vx/scale'
import { AreaClosed } from '@vx/shape'
import { AxisLeft, AxisBottom } from '@vx/axis'
import { extent, min, max, histogram } from 'd3-array'
import gradients from './gradients'
import {kernelDensityEstimator, kernelEpanechnikov} from './kernel-density'

import './main.styl'

class DetritalZirconBase extends Component
  render: ->
    {data} = @props
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
    eachHeight = 60
    height = eachHeight*data.length
    xScale = scaleLinear({
      range: [0, width]
      domain: [0,4000]
    })

    margin = 30
    h 'svg', { width: width+2*margin, height: height+2*margin}, data.map (sampleData, i)->
      {grain_data, sample_id} = sampleData

      xTicks = xScale.ticks(400)
      kde = kernelDensityEstimator(kernelEpanechnikov(50), xTicks)
      fn = (d)->d.best_age
      kdeData = kde(grain_data.map(fn))
      console.log sampleData

      # All KDEs should have same height
      maxProbability = max kdeData, (d)->d[1]

      yScale = scaleLinear({
        range: [eachHeight-10, 0]
        domain: [0, maxProbability]
      })

      labelProps = {label: "Age (Ga)"}
      if i != data.length-1
        labelProps.label = null
        labelProps.tickLabelProps = -> {visibility: 'hidden'}

      id = "gradient_#{i}"
      h 'g', {
        key: sample_id
        transform: "translate(0,#{i*eachHeight})"
      }, [
        h gradients[i], {id}
        createElement 'foreignObject', {x: 0, y: 0, width: 100, height: 50}, (
          h 'h2.sample-name', null, sample_id
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
          tickFormat: (d)->d/1000
          strokeWidth: 1.5
          top: 50
          labelProps...
        }
      ]

DetritalZirconComponent = (props)->
  route = '/api/v1/dz_sample'
  h APIResultView, {route, params: {all: 1}, props...}, (data)->
    h DetritalZirconBase, {data}

export {DetritalZirconComponent}
