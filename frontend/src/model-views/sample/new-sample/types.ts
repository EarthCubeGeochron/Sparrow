interface LOC {
  type: string;
  coordinates: [number, number];
}

interface geo_entity {
  name: string;
  type: string;
}

interface sample_geo_entity {
  ref_datum: string;
  ref_unit: string;
  ref_distance: number;
  geo_entity: geo_entity;
}

interface sampleState {
  embargo_date: Date | null;
  name: string | null;
  location: LOC | null;
  material: string | null;
  depth: number | null;
  elevation: number | null;
  sample_geo_entity: sample_geo_entity[] | null;
  project: object[];
  session: object[];
}

interface sampleFormState extends sampleState {
  changeFunction: stateFunc;
}

type stateFunc = (e) => void;

interface sampleContext {
  sample: sampleFormState;
  dispatch: ({ type, payload }) => any;
}

enum sample_reducer {
  EMBARGO,
  NAME,
  LOCATION,
  MATERIAL,
  DEPTH,
  ELEVATION,
  GEO_ENTITY,
  REMOVE_GEO_ENTITY,
  ADD_SESSION,
  REMOVE_SESSION,
  ADD_PROJECT,
  REMOVE_PROJECT,
  CHANGE_FUNCTION,
  LIST_NAME,
}
enum modelEditList {
  MAIN,
  PROJECT,
  SAMPLE,
  PUBLICATION,
  RESEARCHER,
  SESSION,
}

export {
  modelEditList,
  sample_reducer,
  sampleState,
  sample_geo_entity,
  geo_entity,
  LOC,
  sampleContext,
  sampleFormState,
};
