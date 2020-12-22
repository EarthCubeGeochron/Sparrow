import React, { useReducer } from "react";
/**
 * Reducers to handle the filters on admin list components
 *
 */

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
    // needs to be a remove dispatch, specific for a field
    // needs to be a "clear" dispatch
    default:
      throw new Error("Don't understand action");
  }
}
