# https://bl.ocks.org/mbostock/4341954
import {mean} from 'd3-array'

kernelDensityEstimator = (kernel, X)->
  (V)->
    X.map (x)->
      [x, mean(V, (v)->kernel(x - v))]

kernelEpanechnikov = (k)->
  (v)-> if Math.abs(v /= k) <= 1 then 0.75 * (1 - v * v) / k else 0

export {kernelDensityEstimator, kernelEpanechnikov}
