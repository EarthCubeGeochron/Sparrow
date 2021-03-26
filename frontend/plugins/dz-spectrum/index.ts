/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {Component, createElement} from 'react';
import h from 'react-hyperscript';
import {APIResultView, useAPIResult} from '@macrostrat/ui-components';
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
import { useAPIv2Result } from '~/api-v2';

function DZPlotInner(props) {
  const { ageRange = [0, 4000], data, children, width, height, marginTop = 5, marginBottom = 5 } = props
  let minmax = ageRange

  if (data == null) { return null; }

  const accessor = d => d.value;

  const delta = minmax[1]-minmax[0];
  const bandwidth = 20;
  minmax = [minmax[0] - (bandwidth*4), minmax[1] + (bandwidth*4)];

  const margin = 10;
  const eachHeight = height-marginTop-marginBottom;

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
      children
    ])
  ]);
}

function DetritalZirconComponent(props) {
  const data = useAPIResult( '/datum', {unit: 'Ma', is_accepted: true, ...props} )
  const { session_id } = props;

  if (data == null) { return null; }

  const accessor = d => d.value;

  let minmax = extent(data, accessor);
  const delta = minmax[1]-minmax[0];
  const bandwidth = 20;
  minmax = [minmax[0] - (bandwidth*4), minmax[1] + (bandwidth*4)];

  const margin = 10;
  const marginTop = 10;
  const marginBottom = 50;
  const innerWidth = 750;
  const eachHeight = 150;
  const height = eachHeight+marginTop+marginBottom;
  const width = innerWidth+(2*margin);

  return h(DZPlotInner, { data, width, height, ageRange: minmax, marginTop, marginBottom }, [
    createElement('foreignObject', {x: 0, y: -20, width: 500, height: 50}, (
      h('h4', null, [
        `${data.length} grains`
      ])
    ))
  ]);
}

function DZSessionData({ session_id, date, sample }) {
  const name = sample?.name ?? ""
  const height = 50
  const width = 340
  const data = useAPIResult('/datum', { unit: 'Ma', is_accepted: true, session_id })

  let text = name
  if (data != null) text += " " + `(${data.length} ages)`

  return h("div", [
    h("h5", text),
    h("div.plot-container", {
      style: { height }
    },
      h(DZPlotInner, { session_id, height, width, data })
    )
  ])
}

export {DetritalZirconComponent, DZSessionData};
