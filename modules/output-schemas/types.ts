/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type DecaySystem = "207Pb_235U" | "207Pb_238U" | "206Pb_207Pb" | "208Pb_232Th";

export interface Age {
  value: number;
  error?: number;
  unit?: string;
}
export interface AgeSpectrum {
  sample: SampleModel;
  meta: BaseModel[];
  info: BaseModel[];
  ages: SpectrumAge[];
}
export interface SampleModel {
  name: string;
  id: string;
  igsn?: string;
}
export interface BaseModel {}
export interface SpectrumAge {
  sample: SampleModel;
  meta: BaseModel[];
  info: BaseModel[];
  best_age: UPbAge;
  concordance: number;
}
export interface UPbAge {
  value: number;
  error?: number;
  unit?: string;
  system: DecaySystem;
  age: Age;
}
export interface ConcordiaAge {
  sample: SampleModel;
  meta: BaseModel[];
  info: BaseModel[];
  age206Pb_238U: Age;
  age207Pb_235U: Age;
  age206Pb_207Pb: Age;
}
export interface ConcordiaSpectrum {
  sample: SampleModel;
  meta: BaseModel[];
  info: BaseModel[];
  ages: ConcordiaAge[];
}
export interface DataModel {
  sample: SampleModel;
  meta: BaseModel[];
  info: BaseModel[];
}
export interface Datum {
  value: number;
  error?: number;
  unit: string;
}
export interface DescModel {
  type: string;
}
