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

// This Component uses Intersection Observer to know when an element is being displayed
// And when that item is being displayed state is updated by the reducer callback.

// There are several important variables the application needs to keep track
// of to know how much data is left to load above and below the list:
//      loadingBottom: if data is being loaded, on the case 'start'
//      hasMoreAfter: More to be loaded at bottom
//      after: Point/index in data to load at bottom

const IntergerList = () => {
  const list = [];
  for (let i = 0; i < 100; i++) {
    list.push(i + 1);
  }
  return list;
};

// The reducer handles state updates for the application.
// For the before and after variables there are 3 cases that need to be accounted for:

//      1. When the list is first loaded there are only perPage (15 default) items
//         rendered so the first load will be different than the middle load.

//      2. The middle renders, the list rendered is 25 (default) items long because
//         in order to get the scrolling effect the app renders the newly fetched data
//         plus 10 items that were previously rendered.

//      3. The end of the list there may be less than the perPage(15 default) in the list.

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
  console.log("loading Bottom: " + loadingBottom);
  console.log("After: " + after);
  console.log("Has More After: " + hasMoreAfter);
  console.log(visibleBottom);
  console.log(data);

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
