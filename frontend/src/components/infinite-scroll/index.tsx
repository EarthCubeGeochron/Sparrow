import * as React from "react";
import { useState, useRef, useEffect } from "react";
//import "./ForeverScroll2.css";
import h from "@macrostrat/hyper";
import { useReducer } from "react";
import { createContext } from "react";
import { useContext } from "react";
import { useOnScreen } from "./useOnScreen";
import "./main.styl";

// This Component uses Intersection Observer to know when an element is being displayed
// And when that item is being displayed state is updated by the reducer callback.

// There are several important variables the application needs to keep track
// of to know how much data is left to load above and below the list:
//      loadingBottom: if data is being loaded, on the case 'start'
//      loadingTop: if Data is being loaded at the top, start case
//      hasMoreBefore: More to be loaded at top
//      hasMoreAfter: More to be loaded at bottom
//      before: Point/index in data to load at top
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
    case "startTop":
      return { ...state, loadingTop: true };
    case "loadedTop":
      console.log(action.newData);
      const { newData, newState } = action;
      const after = state.hasMoreAfter
        ? newData >= perPage
          ? state.after - newData.length
          : state.after - perPage
        : state.after - (newData.length + newState.length - newData.length);
      return {
        ...state,
        loadingTop: false,
        data: [...newData, ...newState],
        hasMoreBefore: action.newData.length === perPage,
        before: state.before - action.newData.length,
        after: after,
        hasMoreAfter:
          action.totalData.indexOf(newData.slice(-1)) < action.totalData.length,
      };
    case "loadedBottom":
      console.log(state.after);
      return {
        ...state,
        loadingBottom: false,
        data: [...action.newState, ...action.newData],
        hasMoreAfter: action.newData.length === perPage,
        hasMoreBefore: state.data.length > 0,
        after: state.after + action.newData.length,
      };
    case "setBefore":
      return {
        ...state,
        before: action.totalData.indexOf(state.data[0]),
      };
    default:
      throw new Error("Don't understand action");
  }
};
const perPage = 15;

// initialize context
const MyContext = createContext({});

// context is made of a Provider and a Consumer
// in Provider will add other values to state object to be updated by different reducer cases to handle top loading
function Provider({ children }) {
  const [state, dispatch] = useReducer(reducer, {
    loadingBottom: false,
    loadingTop: false,
    hasMoreAfter: true,
    hasMoreBefore: false,
    data: [],
    after: 0,
    before: 0,
  });

  // List of Data that the application references for indexes
  const totalData = IntergerList();

  const loadBottom = () => {
    dispatch({ type: "startBottom" });

    const newData = totalData.slice(after, after + perPage);
    const newState = state.data.slice(-10);
    const lastNumber = totalData.slice(-1);

    dispatch({ type: "loadedBottom", newData, newState, totalData });
    dispatch({ type: "setBefore", totalData });
  };
  const loadTop = () => {
    dispatch({ type: "startTop" });

    const newData =
      before < perPage
        ? totalData.slice(0, before)
        : totalData.slice(before - perPage, before);

    const newState = state.data.slice(0, 10);
    dispatch({ type: "loadedTop", newData, newState, totalData });
  };

  const {
    loadingBottom,
    loadingTop,
    hasMoreBefore,
    data,
    after,
    before,
    hasMoreAfter,
  } = state;

  return (
    <MyContext.Provider
      value={{
        loadingBottom,
        loadingTop,
        loadBottom,
        loadTop,
        hasMoreAfter,
        hasMoreBefore,
        before,
        after,
        data,
      }}
    >
      {children}
    </MyContext.Provider>
  );
}

function ForeverScroll() {
  const {
    loadingBottom,
    loadBottom,
    loadTop,
    loadingTop,
    data,
    hasMoreAfter,
    hasMoreBefore,
    before,
    after,
  } = useContext(MyContext);

  const [setBottom, visibleBottom] = useOnScreen({
    threshold: 1,
  });
  const [setTop, visibleTop] = useOnScreen({ rootMargin: "300px" });

  console.log(before);
  console.log(after);
  console.log(data);
  console.log(hasMoreAfter);
  console.log(visibleBottom);

  useEffect(() => {
    if (visibleBottom) {
      loadBottom();
    }
    if (visibleTop) {
      loadTop();
    }
  }, [visibleBottom, visibleTop]);

  return (
    <div className="ForeverScroll">
      {!loadingTop && !loadingBottom && hasMoreBefore && (
        <div ref={setTop}></div>
      )}
      {loadingTop && <h4>Loading...</h4>}

      <ul>
        {data.map((number) => (
          <h4 key={number} style={{ backgroundColor: "aquamarine" }}>
            {number}
          </h4>
        ))}

        {loadingBottom && <h4>Loading...</h4>}

        {!loadingBottom && hasMoreAfter && <div ref={setBottom}></div>}
      </ul>
    </div>
  );
}

export default () => {
  return (
    <Provider>
      <ForeverScroll />
    </Provider>
  );
};
