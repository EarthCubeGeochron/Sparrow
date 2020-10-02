import * as React from "react";
import { useState, useRef, useEffect } from "react";
import h from "@macrostrat/hyper";
import { useReducer } from "react";
import { createContext } from "react";
import { useContext } from "react";
import { useOnScreen } from "./useOnScreen";
import "./main.styl";
import { useAPIResult } from "@macrostrat/ui-components";
import { ProjectInfoLink } from "~/model-views/project";


/**
 * How do I make this virtualized?
 * 
 * Need to know height of items: need a callback for each item useElementDimensions?
 * The height of the ENTIRE list once rendered
 * A measurement that shows how far the list has scrolled
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
 * This Component uses Intersection Observer to know when an element is being displayed
 *  And when that item is being displayed state is updated by the reducer callback.
 * @param initialData: An array of data that can be mapped into the component provided
 * @param component: A component that can take in the mapped data and format it into what the user wants to display
 *
 */
function ForeverScroll({ initialData, component }) {
  const [state, dispatch] = useReducer(reducer, {
    loadingBottom: false,
    hasMoreAfter: true,
    data: [],
    after: 0,
  });
  const [setBottom, visibleBottom] = useOnScreen();

  // List of Data that the application references for indexes
  const totalData = initialData;
  console.log(totalData);

  const loadBottom = () => {
    dispatch({ type: "startBottom" });

    const newData = totalData.slice(after, after + perPage);

    dispatch({ type: "loadedBottom", newData });
  };

  const { loadingBottom, data, after, hasMoreAfter } = state;
  // console.log("loading Bottom: " + loadingBottom);
  // console.log("After: " + after);
  // console.log("Has More After: " + hasMoreAfter);
  // console.log(visibleBottom);
  // console.log(data);

  useEffect(() => {
    if (visibleBottom) {
      loadBottom();
    }
  }, [visibleBottom]);

  return (
    <div className="ForeverScroll" style={{ marginTop: "20px" }}>
      {data.map((d) => h(component, d))}

      {hasMoreAfter && (
        <div ref={setBottom} style={{ marginTop: "50px" }}>
          This is where it Refreshes
        </div>
      )}
    </div>
  );
}

export default ForeverScroll;
