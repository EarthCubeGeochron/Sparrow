/**
 * Reducers to handle the filters on admin list components
 *
 */

function objectFilter(obj, predicate) {
  const newObject = Object.fromEntries(Object.entries(obj).filter(predicate));
  return newObject;
}

////////// action types ///////////////////

type SetDateRange = { type: "set-date-range"; dates: [string, string] };
type SetPublic = { type: "set-public"; embargoed: boolean };
type SetDoiLike = { type: "set-doi-like"; doi_like: string };
type SetGeometry = { type: "set-geometry"; geometry: string };
type SetSearch = { type: "set-search"; search: string };
type RemoveFilter = { type: "remove-filter"; field: string };

type ToggleOpen = { type: "toggle-open" };

type FilterActions =
  | SetDateRange
  | SetPublic
  | SetDoiLike
  | SetGeometry
  | SetSearch
  | RemoveFilter
  | ToggleOpen;

interface ParamsI {
  date_range?: string;
  public?: boolean;
  doi_like?: string;
  geometry?: string; //WKT
  search?: string;
}

export interface FilterState {
  params: ParamsI;
  isOpen: boolean;
}

export function reducer(state: FilterState, action: FilterActions) {
  switch (action.type) {
    case "set-date-range":
      // do some logic here to prepare params
      return {
        ...state,
        params: {
          ...state.params,
          date_range: action.dates,
        },
      };
    case "set-public":
      return {
        ...state,
        params: {
          ...state.params,
          public: action.embargoed,
        },
      };
    case "set-doi-like":
      return {
        ...state,
        params: {
          ...state.params,
          doi_like: action.doi_like,
        },
      };
    case "set-geometry":
      return {
        ...state,
        params: {
          ...state.params,
          geometry: action.geometry,
        },
      };
    case "set-search":
      if (action.search == "") {
        const params = { ...state.params };
        delete params["search"];
        return {
          ...state,
          params: params,
        };
      }
      return {
        ...state,
        params: {
          ...state.params,
          search: action.search,
        },
      };
    case "remove-filter":
      let param = action.field;
      const newParams = objectFilter(
        state.params,
        ([key, value]) => key != param
      );
      return {
        ...state,
        params: newParams,
      };
    case "toggle-open":
      return {
        ...state,
        isOpen: !state.isOpen,
        params: { ...state.params },
      };
    default:
      throw new Error("Don't understand action");
  }
}

export { FilterActions };
