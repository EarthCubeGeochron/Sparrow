/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS101: Remove unnecessary use of Array.from
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {render} from 'react-dom';
import {Component} from 'react';
import h from 'react-hyperscript';
import styled from '@emotion/styled';
import { scaleLinear } from '@vx/scale';
import { AreaClosed } from '@vx/shape';
import { AxisLeft, AxisBottom } from '@vx/axis';
import { APIResultView } from '@macrostrat/ui-components';
import { min, max, extent } from 'd3-array';
import T from 'prop-types';

let d = styled.div`\
min-height: 200px;
width: 10%;
background: purple;
margin-bottom: 1em;\
`;

const errorExtent = function(arr){
  const mn = min(arr, d => d.value - d.error);
  const mx = max(arr, d => d.value + d.error);
  return [mn, mx];
};

class StepHeatingChart extends Component {
  constructor(props){
    super(props);
    this.findPlateauAge = this.findPlateauAge.bind(this);
    this.renderChart = this.renderChart.bind(this);
  }

  findPlateauAge(data){
    const interpretedAges = data.filter(d => d.session_index == null);
    // Find plateau age
    for (let a of Array.from(interpretedAges)) {
      for (let datum of Array.from(a.data)) {
        if (datum.parameter === 'plateau_age') {
          return datum;
        }
      }
    }
  }

  renderChart(data){
    const width = 800;
    const height = 450;

    const margin = 50;
    const innerWidth = width-(2*margin);
    const innerHeight = height-(2*margin);

    const heatingSteps = data.filter(d => d.session_index != null);
    heatingSteps.sort((a, b) => b.session_index-a.session_index);


    const ages = heatingSteps.map(d => ({
      in_plateau: !d.is_bad,
      age: d.data.find(v => v.parameter === 'step_age')
    }));
    const plateauAge = this.findPlateauAge(data);
    let plateauIx = [];
    for (let i = 0; i < ages.length; i++) {
      d = ages[i];
      if (d.in_plateau) { plateauIx.push(i); }
    }
    plateauIx = extent(plateauIx);


    const yExtent = errorExtent(ages.map(d => d.age));

    const xScale = scaleLinear({
      range: [0, innerWidth],
      domain: [0, heatingSteps.length]
    });

    const yScale = scaleLinear({
      range: [innerHeight, 0],
      domain: yExtent
    });

    const deltaX = xScale(1)-xScale(0);

    return h('svg.step-heating-chart', {
      width: 900, height
    }, [
      h('g.chart-main', {
        transform: `translate(${margin},${margin})`
      }, [
        h('g.data-area', [
          h('g.heating-steps', ages.map(function(d,i){
            const {age, in_plateau} = d;
            const mn = age.value-age.error;
            const mx = age.value+age.error;
            const y = yScale(mx);

            return h('rect', {
              x: xScale(i),
              y,
              width: deltaX,
              height: yScale(mn)-y,
              fill: in_plateau ? "#444" : "#aaa"
            });})),
          h('g.plateau-age', [
            h('rect', {
              x: xScale(plateauIx[0]),
              y: yScale(plateauAge.value+plateauAge.error),
              width: deltaX*((1+plateauIx[1])-plateauIx[0]),
              height: yScale(0)-yScale(2*plateauAge.error),
              stroke: '#222',
              'stroke-width': '2px',
              fill: 'transparent'
            })
          ])
        ]),
        h(AxisBottom, {
          scale: xScale,
          numTicks: 10,
          top: innerHeight,
          label: "Heating step"
        }),
        h(AxisLeft, {
          scale: yScale,
          numTicks: 10,
          label: "Age (Ma)"
        })
      ])
    ]);
  }

  render() {
    const {session_id} = this.props;
    console.log(session_id);
    return h(APIResultView, {
      route: "/analysis",
      params: {session_id}
    }, this.renderChart);
  }
}


export {StepHeatingChart};