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
import md from './plateau-ages.md';
import './main.styl';

const ResponsiveHistogram = withParentSize(({ parentWidth, parentHeight, ...rest}) => h(Histogram, {
  width: parentWidth,
  height: parentHeight,
  ...rest
}));

class AgeChart extends Component {
  render() {
    let {data, width, range} = this.props;
    if (data == null) { return null; }
    if (range == null) { range = [0,2000]; }

    const rawData = data.map(d => d.value)
      .filter(d => d > range[0])
      .filter(d => d < range[1]);

    return h(ResponsiveHistogram, {
      ariaLabel: "Histogram of ages",
      orientation: "vertical",
      cumulative: false,
      normalized: false,
      binCount: 50,
      valueAccessor(datum){ return datum; },
      binType: "numeric",
      limits: range
    }, [
      h(BarSeries, {animated: true, rawData, fill: '#0f9960', stroke: '#0a6640'}),
      h(XAxis, {label: "Age"}),
      h(YAxis, {label: "Measurements"})
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
    const params = {
      unit: 'Ma',
      parameter: 'plateau_age',
      technique: "Ar/Ar Incremental Heating"
    };

    const min = 0;
    const max = 2000;
    const labelRenderer = function(v){
      if (v < 1000) {
        return `${v} Ma`;
      }
      v /= 1000;
      return `${v} Ga`;
    };

    return h(APIResultView, {route: '/datum', params}, data=> {
      if (data == null) { return null; }
      return h('div.age-chart-container', [
        h(Callout, {
          icon: 'scatter-plot', title: "Plateau ages"
        }, [
          h('p', "All of the plateau ages ingested into the lab data system"),
          h('div.controls', [
            h('h4', 'Age range'),
            h(RangeSlider, {
              value: this.state.range, min, max,
              labelStepSize: 200,
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
        h('div.chart-container', {style: {height: 460}}, [
          h(AgeChart, {data, range})
        ])
      ]);
  });
  }
}

class PlateauAgesComponent extends Component {
  render() {
    return h('div.data-view#age-chart', [
      h(ChartOuter)
    ]);
  }
}


export {PlateauAgesComponent};
