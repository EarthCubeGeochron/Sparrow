#http://localhost:3000/api/v1/datum?unit=Ma&parameter=plateau_age&technique=Ar%2FAr%20Fusion
import h from 'react-hyperscript'
import {Component} from 'react'
import {Callout, Icon, RangeSlider} from '@blueprintjs/core'
import {APIResultView} from '@macrostrat/ui-components'
import { scaleLinear } from '@vx/scale'
import { Histogram, DensitySeries, BarSeries, withParentSize, XAxis, YAxis } from '@data-ui/histogram';
import md from './plateau-ages.md'
import './main.styl'

ResponsiveHistogram = withParentSize ({ parentWidth, parentHeight, ...rest})->
  h Histogram, {
    width: parentWidth
    height: parentHeight
    rest...
  }

class AgeChart extends Component
  render: ->
    {data, width, range} = @props
    return null unless data?
    range ?= [0,2000]

    #renderTooltip = ({ event, datum, data, color }) => (
      #h 'div', [
        #h 'strong', {style: {color}}, "#{datum.bin0} to #{datum.bin1}"
          #<div><strong>count </strong>{datum.count}</div>
          #<div><strong>cumulative </strong>{datum.cumulative}</div>
          #<div><strong>density </strong>{datum.density}</div>
      #]
      #

    rawData = data.map (d)->d.value
      .filter (d)-> d > range[0]
      .filter (d)-> d < range[1]

    h ResponsiveHistogram, {
      ariaLabel: "Histogram of ages"
      orientation: "vertical"
      cumulative: false
      normalized: false
      binCount: 50
      valueAccessor: (datum)->datum
      binType: "numeric"
      limits: range
    }, [
      h BarSeries, {animated: true, rawData, fill: '#0f9960', stroke: '#0a6640'}
      h XAxis, {label: "Age"}
      h YAxis, {label: "Measurements"}
    ]

class ChartOuter extends Component
  constructor: (props)->
    super props
    @state = {
      range: [0, 1500]
    }
  render: ->
    {range} = @state
    params = {
      unit: 'Ma'
      parameter: 'plateau_age'
      technique: "Ar/Ar Incremental Heating"
    }

    min = 0
    max = 2000
    labelRenderer = (v)->
      if v < 1000
        return "#{v} Ma"
      v /= 1000
      return "#{v} Ga"

    h APIResultView, {route: '/datum', params}, (data)=>
      return null unless data?
      h 'div.age-chart-container', [
        h Callout, {
          icon: 'scatter-plot', title: "Plateau ages"
        }, [
          h 'p', "All of the plateau ages ingested into the lab data system"
          h 'div.controls', [
            h 'h4', 'Age range'
            h RangeSlider, {
              value: @state.range, min, max
              labelStepSize: 200
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

class PlateauAgesComponent extends Component
  render: ->
    h 'div.data-view#age-chart', [
      h ChartOuter
    ]


export {PlateauAgesComponent}
