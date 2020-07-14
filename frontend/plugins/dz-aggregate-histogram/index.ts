/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
//http://localhost:3000/api/v1/datum?unit=Ma&parameter=plateau_age&technique=Ar%2FAr%20Fusion
import h from 'react-hyperscript';
import {Component} from 'react';
import {Callout, Icon, RangeSlider} from '@blueprintjs/core';
import {APIResultView} from '@macrostrat/ui-components';
import { scaleLinear } from '@vx/scale';
import { Histogram, DensitySeries, BarSeries, withParentSize, XAxis, YAxis } from '@data-ui/histogram';
import {sum} from 'd3-array';

const ResponsiveHistogram = withParentSize(({ parentWidth, parentHeight, ...rest}) => h(Histogram, {
  width: parentWidth,
  height: parentHeight,
  ...rest
}));

class AgeChart extends Component {
  render() {
    let {data, width, range} = this.props;
    if (range == null) { range = [0,2000]; }
    if (data == null) { return; }
    data = data.filter(d => (d.min_age >= range[0]) && (d.max_age <= range[1]));

    let binnedData = data.map(function(d, i){
      const {count} = d;
      return {id: i, bin0: d.min_age, bin1: d.max_age, count};});

    const v = Math.floor(binnedData.length/100);
    if (v > 1) {
      const bd2 = [];
      for (let i = 0; i < binnedData.length; i++) {
        const d = binnedData[i];
        console.log(Math.floor(i/v));
        if ((i%v) === 0) {
          bd2.push(d);
          continue;
        }
        bd2[Math.floor(i/v)]['bin1'] = d.bin1;
        bd2[Math.floor(i/v)]['count'] += d.count;
      }
      console.log(bd2);

      binnedData = bd2;
    }

    return h(ResponsiveHistogram, {
      ariaLabel: "Histogram of ages",
      orientation: "vertical",
      cumulative: false,
      normalized: false,
      valueAccessor(datum){ return datum; },
      binType: "numeric",
      limits: range
    }, [
      h(BarSeries, {
        animated: true, binnedData,
        fill: '#f1f1f1', stroke: '#f5e1da'}),
      h(DensitySeries, {
        animated: false, binnedData,
        fill: '#49beb7', stroke: '#085f63'}),
      h(XAxis, {label: "Age (Ma)"}),
      h(YAxis, {label: "Number of grains"})
    ]);
  }
}

class ChartOuter extends Component {
  constructor(props){
    super(props);
    this.state = {
      range: [0, 1500]
    };
  }
  render() {
    const {range} = this.state;

    const min = 0;
    const max = 4500;
    const labelRenderer = function(v){
      if (v < 1000) {
        return `${v} Ma`;
      }
      v /= 1000;
      return `${v} Ga`;
    };

    const params = {all: true};
    return h(APIResultView, {route: '/aggregate_histogram', params}, data=> {
      if (data == null) { return null; }
      const num = sum(data, d => d.count);

      return h('div.age-chart-container', [
        h(Callout, {
          icon: 'scatter-plot', title: "Accepted ages"
        }, [
          h('p', `${num} accepted ages ingested into the lab data system`),
          h('div.controls', [
            h('h4', 'Age range'),
            h(RangeSlider, {
              value: this.state.range,
              min, max,
              labelStepSize: 500,
              labelRenderer,
              onChange: range=> {
                console.log(range);
                if ((range[1]-range[0]) < 5) {
                  range[1] = range[0]+5;
                }
                return this.setState({range});
              }
            })
          ])
        ]),
        h('div.chart-container', {style: {height: 500}}, [
          h(AgeChart, {data, range})
        ])
      ]);
  });
  }
}

class AggregateHistogram extends Component {
  render() {
    return h('div.data-view#age-chart', [
      h(ChartOuter)
    ]);
  }
}


export {AggregateHistogram};
