#http://localhost:3000/api/v1/datum?unit=Ma&parameter=plateau_age&technique=Ar%2FAr%20Fusion
import h from 'react-hyperscript'
import {Component} from 'react'
import {Callout, Icon} from '@blueprintjs/core'
import {APIResultView} from '@macrostrat/ui-components'
import { scaleLinear } from '@vx/scale'
import { Histogram, DensitySeries, BarSeries, withParentSize, XAxis, YAxis } from '@data-ui/histogram';

ResponsiveHistogram = withParentSize ({ parentWidth, parentHeight, ...rest})->
  h Histogram, {
    width: parentWidth
    height: parentHeight
    rest...
  }

class AgeChart extends Component
  render: ->
    {data, width} = @props
    return null unless data?

    #renderTooltip = ({ event, datum, data, color }) => (
      #h 'div', [
        #h 'strong', {style: {color}}, "#{datum.bin0} to #{datum.bin1}"
          #<div><strong>count </strong>{datum.count}</div>
          #<div><strong>cumulative </strong>{datum.cumulative}</div>
          #<div><strong>density </strong>{datum.density}</div>
      #]

    rawData = data.map (d)->d.value

    h ResponsiveHistogram, {
      ariaLabel: "Histogram of ages"
      orientation: "vertical"
      cumulative: false
      normalized: true
      binCount: 50
      valueAccessor: (datum)->datum
      binType: "numeric"
    }, [
      h BarSeries, {animated: true, rawData}
      h XAxis
      h YAxis
    ]

ChartOuter = (props)->
  route = "http://localhost:3000/api/v1/datum"
  params = {
    unit: 'Ma'
    parameter: 'plateau_age'
    technique: "Ar/Ar Incremental Heating"
  }
  h APIResultView, {route, params}, (data)->
    h 'div.age-chart-container', {style: {height: 600}}, [
      h AgeChart, {data}
    ]

class AgeChartComponent extends Component
  @defaultProps: {
    apiEndpoint: '/api/v1/session'
  }
  render: ->
    {apiEndpoint} = @props

    h 'div.data-view#age-chart', [
      h Callout, {
        icon: 'scatter-plot', title: "Plateau ages"
      }, "All of the plateau ages ingested into the lab data system"
      h ChartOuter
    ]

export {AgeChartComponent}

