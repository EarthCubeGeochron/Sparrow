import { sample_reducer } from "./types";

const sampleReducer = (state, action) => {
  switch (action.type) {
    case sample_reducer.EMBARGO:
      return {
        ...state,
        embargo_date: action.payload.embargo_date,
      };
    case sample_reducer.NAME:
      return {
        ...state,
        name: action.payload.name,
      };
    case sample_reducer.MATERIAL:
      return {
        ...state,
        material: action.payload.material,
      };
    case sample_reducer.DEPTH:
      return {
        ...state,
        depth: action.payload.depth,
      };
    case sample_reducer.ELEVATION:
      return {
        ...state,
        elevation: action.elevation,
      };
    case sample_reducer.LOCATION:
      const { lat, lon } = action.payload.coordinates;
      const coordinates = [lon, lat];
      return {
        ...state,
        location: { type: "Point", coordinates: coordinates },
      };
    case sample_reducer.GEO_ENTITY:
      const SampleGeoEntitys = [
        ...state.sample_geo_entity,
        ...new Array(action.payload.geo_entity),
      ];
      return {
        ...state,
        sample_geo_entity: SampleGeoEntitys,
      };
    case sample_reducer.ADD_PROJECT:
      const projects = [...state.project, ...new Array(action.payload.project)];
      return {
        ...state,
        project: projects,
      };
    case sample_reducer.REMOVE_PROJECT:
      const id = action.payload.project.id!;
      const currentProjects = [...state.project];
      const newProjects = currentProjects.filter((ele) => ele.id != id);
      return {
        ...state,
        project: newProjects,
      };
    case sample_reducer.ADD_SESSION:
      const sessions = [...state.session, ...new Array(action.payload.session)];
      return {
        ...state,
        session: sessions,
      };
    case sample_reducer.REMOVE_SESSION:
      const { id: ss_id } = action.payload.session;
      const currentSs = [...state.session];
      const newSs = currentSs.filter((ele) => ele.id != ss_id);
      return {
        ...state,
        session: newSs,
      };
    case sample_reducer.CHANGE_FUNCTION:
      return {
        ...state,
        changeFunction: action.payload.changeFunction,
      };
    case sample_reducer.LIST_NAME:
      return {
        ...state,
        listName: action.payload.listName,
      };
    default:
      throw new Error("What does this mean?");
  }
};
export { sampleReducer };
