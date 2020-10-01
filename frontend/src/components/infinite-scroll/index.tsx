import * as React from "react";
import { useState, useRef, useEffect } from "react";
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
//      hasMoreAfter: More to be loaded at bottom
//      after: Point/index in data to load at bottom

const IntergerList = () => {
  const list = [];
  for (let i = 0; i < 100; i++) {
    list.push(i + 1);
  }
  return list;
};

const reducer = (state, action) => {
  switch (action.type) {
    case "startBottom":
      return { ...state, loadingBottom: true };
    case "loadedBottom":
      console.log(state.after);
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

// initialize context
const MyContext = createContext();

// context is made of a Provider and a Consumer
// in Provider will add other values to state object to be updated by different reducer cases to handle top loading
function Provider({ children }) {
  const [state, dispatch] = useReducer(reducer, {
    loadingBottom: false,
    hasMoreAfter: true,
    data: [],
    after: 0,
  });

  // List of Data that the application references for indexes
  const totalData = IntergerList();

  const loadBottom = () => {
    dispatch({ type: "startBottom" });

    const newData = totalData.slice(after, after + perPage);

    dispatch({ type: "loadedBottom", newData, totalData });
  };

  const { loadingBottom, data, after, hasMoreAfter } = state;

  return (
    <MyContext.Provider
      value={{
        loadingBottom,
        loadBottom,
        hasMoreAfter,
        after,
        data,
      }}
    >
      {children}
    </MyContext.Provider>
  );
}

function ForeverScroll() {
  const { loadingBottom, loadBottom, data, hasMoreAfter, after } = useContext(
    MyContext
  );

  const [setBottom, visibleBottom] = useOnScreen({
    threshold: 1,
  });

  console.log("STARTS HERE");
  console.log("After: " + after);
  console.log(data);

  useEffect(() => {
    if (visibleBottom) {
      loadBottom();
    }
  }, [visibleBottom]);

  return (
    <div className="ForeverScroll">
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
