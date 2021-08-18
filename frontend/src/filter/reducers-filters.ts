/**
 * Reducers to handle the filters on admin list components
 *
 */

function objectFilter(obj, predicate) {
  //const { obj, predicate } = props;
  const newObject = Object.fromEntries(Object.entries(obj).filter(predicate));
  return newObject;
}

export function reducer(state, action) {
  switch (action.type) {
    case "date_range":
      // do some logic here to prepare params
      return {
        ...state,
        date_range: action.payload.dates,
      };
    case "public":
      return {
        ...state,
        public: action.payload.embargoed,
      };
    case "doi_like":
      return {
        ...state,
        doi_like: action.payload.doi_like,
      };
    case "geometry":
      return {
        ...state,
        geometry: action.payload.geometry,
      };
    case "search":
      return {
        ...state,
        search: action.payload.search,
      };
    case "removeSingle":
      let param = action.payload.field;
      const newState = objectFilter(state, ([key, value]) => key != param);
      return {
        ...newState,
      };
    default:
      throw new Error("Don't understand action");
  }
}
