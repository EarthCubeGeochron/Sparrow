# https://bl.ocks.org/mbostock/4341954
import {mean} from 'd3-array'

kernelDensityEstimator = (kernel, X)->
  (V)->
    X.map (x)->
      [x, mean(V, (v)->kernel(x - v))]

kernelGaussian = (k)->
  (v)->
    v /= k
    1 / Math.sqrt(2 * Math.PI) * Math.exp(-.5 * v * v) / k

kernelEpanechnikov = (k)->
  (v)-> if Math.abs(v /= k) <= 1 then 0.75 * (1 - v * v) / k else 0

export {kernelDensityEstimator, kernelEpanechnikov, kernelGaussian}
