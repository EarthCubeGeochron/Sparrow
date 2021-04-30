import { mean } from "d3-array";

const kernelDensityEstimator = (kernel, X) => (V) =>
  X.map((x) => [x, mean(V, (v) => kernel(x - v))]);

const kernelGaussian = (k) =>
  function (v) {
    v /= k;
    return ((1 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * v * v)) / k;
  };

const kernelEpanechnikov = (k) =>
  function (v) {
    if (Math.abs((v /= k)) <= 1) {
      return (0.75 * (1 - v * v)) / k;
    } else {
      return 0;
    }
  };

export { kernelDensityEstimator, kernelEpanechnikov, kernelGaussian };
