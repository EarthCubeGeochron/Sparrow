import React, { useReducer } from "react";
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
    case "removeSingle":
      let param = action.payload.field;
      const newState = objectFilter(state, ([key, value]) => key != param);
      console.log(state);
      return {
        ...newState,
      };
    // needs to be a remove dispatch, specific for a field
    // needs to be a "clear" dispatch
    default:
      throw new Error("Don't understand action");
  }
}
