#http://localhost:3000/api/v1/datum?unit=Ma&parameter=plateau_age&technique=Ar%2FAr%20Fusion
import h from 'react-hyperscript'
import {Component} from 'react'
import {Callout, Icon, RangeSlider} from '@blueprintjs/core'
import {APIResultView} from '@macrostrat/ui-components'
import { scaleLinear } from '@vx/scale'
import { Histogram, DensitySeries, BarSeries, withParentSize, XAxis, YAxis } from '@data-ui/histogram';
import {sum} from 'd3-array'

ResponsiveHistogram = withParentSize ({ parentWidth, parentHeight, ...rest})->
  h Histogram, {
    width: parentWidth
    height: parentHeight
    rest...
  }

class AgeChart extends Component
  render: ->
    {data, width, range} = @props
    range ?= [0,2000]
    return unless data?
    data = data.filter (d)->
      d.min_age >= range[0] and d.max_age <= range[1]

    binnedData = data.map (d, i)->
      {count} = d
      {id: i, bin0: d.min_age, bin1: d.max_age, count}

    v = binnedData.length//100
    if v > 1
      bd2 = []
      for d,i in binnedData
        console.log i//v
        if i%v == 0
          bd2.push d
          continue
        bd2[i//v]['bin1'] = d.bin1
        bd2[i//v]['count'] += d.count
      console.log bd2

      binnedData = bd2

    h ResponsiveHistogram, {
      ariaLabel: "Histogram of ages"
      orientation: "vertical"
      cumulative: false
      normalized: false
      valueAccessor: (datum)->datum
      binType: "numeric"
      limits: range
    }, [
      h BarSeries, {
        animated: true, binnedData,
        fill: '#f1f1f1', stroke: '#f5e1da'}
      h DensitySeries, {
        animated: false, binnedData,
        fill: '#49beb7', stroke: '#085f63'}
      h XAxis, {label: "Age (Ma)"}
      h YAxis, {label: "Number of grains"}
    ]

class ChartOuter extends Component
  constructor: (props)->
    super props
    @state = {
      range: [0, 1500]
    }
  render: ->
    {range} = @state

    min = 0
    max = 4500
    labelRenderer = (v)->
      if v < 1000
        return "#{v} Ma"
      v /= 1000
      return "#{v} Ga"

    params = {all: true}
    h APIResultView, {route: '/aggregate_histogram', params}, (data)=>
      return null unless data?
      num = sum(data, (d)->d.count)

      h 'div.age-chart-container', [
        h Callout, {
          icon: 'scatter-plot', title: "Accepted ages"
        }, [
          h 'p', "#{num} accepted ages ingested into the lab data system"
          h 'div.controls', [
            h 'h4', 'Age range'
            h RangeSlider, {
              value: @state.range,
              min, max
              labelStepSize: 500
              labelRenderer
              onChange: (range)=>
                console.log range
                if range[1]-range[0] < 5
                  range[1] = range[0]+5
                @setState {range}
            }
          ]
        ]
        h 'div.chart-container', {style: {height: 500}}, [
          h AgeChart, {data, range}
        ]
      ]

class AggregateHistogram extends Component
  render: ->
    h 'div.data-view#age-chart', [
      h ChartOuter
    ]


export {AggregateHistogram}
