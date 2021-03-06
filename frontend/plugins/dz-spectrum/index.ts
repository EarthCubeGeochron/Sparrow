/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {Component, createElement} from 'react';
import h from 'react-hyperscript';
import {APIResultView} from '@macrostrat/ui-components';
import { scaleLinear } from '@vx/scale';
import { AreaClosed } from '@vx/shape';
import { AxisLeft, AxisBottom } from '@vx/axis';
import { extent, min, max, histogram } from 'd3-array';
import gradients from './gradients';
import {
  kernelDensityEstimator,
  kernelEpanechnikov,
  kernelGaussian
} from './kernel-density';

import './main.styl';

class DetritalZirconBase extends Component {
  render() {
    const {data, session_id} = this.props;
    if (data == null) { return null; }

    const accessor = d => d.value;

    let minmax = extent(data, accessor);
    const delta = minmax[1]-minmax[0];
    const bandwidth = delta/50;
    minmax = [minmax[0] - (bandwidth*4), minmax[1] + (bandwidth*4)];

    const hist = histogram()
      .domain(minmax)
      .thresholds(80)
      .value(accessor);

    const margin = 10;
    const marginTop = 10;
    const marginBottom = 50;
    const innerWidth = 750;
    const eachHeight = 150;
    const height = eachHeight+marginTop+marginBottom;
    const width = innerWidth+(2*margin);

    const xScale = scaleLinear({
      range: [0, width],
      domain: minmax
    });

    let label = "Age (Ma)";
    let tickFormat = d => d;
    if (delta > 1000) {
      label = "Age (Ga)";
      tickFormat = d => d/1000;
    }


    const xTicks = xScale.ticks(400);
    const kde = kernelDensityEstimator(kernelGaussian(bandwidth), xTicks);
    const kdeData = kde(data.map(accessor));

    // All KDEs should have same height
    const maxProbability = max(kdeData, d => d[1]);

    const yScale = scaleLinear({
      range: [eachHeight, 0],
      domain: [0, maxProbability]
    });

    const labelProps = {label};

    const id = "gradient_1";

    return h('svg', { width, height}, [
      h('g', {
        transform: `translate(${margin},${marginTop})`
      }, [
        h(gradients[0], {id}),
        h(AreaClosed, {
          data: kdeData,
          yScale,
          x(d){ return xScale(d[0]); },
          y(d){ return yScale(d[1]); },
          fill: `url(#${id})`
        }),
        h(AxisBottom, {
          scale: xScale,
          numTicks: 10,
          tickLength: 4,
          tickFormat,
          strokeWidth: 1.5,
          top: eachHeight,
          ...labelProps
        }),
        createElement('foreignObject', {x: 0, y: -20, width: 500, height: 50}, (
          h('h4', null, [
            `${data.length} grains`
          ])
        )
        )
      ])
    ]);
  }
}

const DetritalZirconComponent = function(props){
  const route = '/datum';
  return h(APIResultView, {
    route,
    params: {unit: 'Ma', is_accepted: true, ...props}
  }, data => h(DetritalZirconBase, {data, ...props}));
};

export {DetritalZirconComponent};
