import * as React from "react";
import { useState, useRef, useEffect } from "react";
import h from "@macrostrat/hyper";
import { useReducer } from "react";
import { useOnScreen } from "./useOnScreen";
import "./main.styl";
import { Spinner } from "@blueprintjs/core";

/**
 * How do I make this virtualized?
 *
 * Need to know height of items: need a callback for each item useElementDimensions?
 * The height of the ENTIRE list once rendered (innerHeight)
 * A measurement that shows how far the list has scrolled
 *
 * How to know when items intersect top and bottom of list:
 *  divide pixel position of item by height of items. Math.floor() turns pixel position into index
 *
 *
 */

const reducer = (state, action) => {
  switch (action.type) {
    case "startBottom":
      return { ...state, loadingBottom: true };
    case "loadedBottom":
      return {
        ...state,
        loadingBottom: false,
        data: [...state.data, ...action.newData],
        hasMoreAfter: action.newData.length === perPage,
        after: state.after + action.newData.length,
      };
    default:
      throw new Error("Don't understand action");
  }
};
const perPage = 15;

/**
 *
 * @description This component uses Intersection Observer to know when an element is being displayed
 *  And when that item is being displayed state is updated by the reducer callback.
 * @param {string[]}initialData: An array of data that can be mapped into the component provided. Array of Objects
 * @param component: A component that can take in the mapped data and format it into what the user wants to display
 * @param {function} fetch A function that will call an API to fetch the next page of data when intersection is observed
 */
function ForeverScroll({ initialData, component, fetch }) {
  const [state, dispatch] = useReducer(reducer, {
    loadingBottom: false,
    hasMoreAfter: true,
    data: [],
    after: 0,
  });
  const [setBottom, visibleBottom] = useOnScreen();

  // List of Data that the application references for indexes
  const totalData = initialData;
  //console.log(totalData);

  const loadBottom = () => {
    dispatch({ type: "startBottom" });

    // api call to fetch more data

    const newData = totalData.slice(after, after + perPage);

    dispatch({ type: "loadedBottom", newData });
  };

  const { loadingBottom, data, after, hasMoreAfter } = state;

  useEffect(() => {
    if (visibleBottom) {
      loadBottom();
      fetch();
    }
  }, [visibleBottom]);

  return (
    <div className="ForeverScroll" style={{ marginTop: "20px" }}>
      {data.map((d) => h(component, d))}

      {loadingBottom && h(Spinner)}

      {hasMoreAfter && (
        <div ref={setBottom} style={{ marginTop: "50px" }}>
          This is where it Refreshes
        </div>
      )}
    </div>
  );
}

export default ForeverScroll;
