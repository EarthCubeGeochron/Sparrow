/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS206: Consider reworking classes to avoid initClass
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import React, {
  Component,
  createContext,
  useContext,
  useState,
  Children,
  ReactNode,
} from "react";
import { ErrorBoundary } from "../util";
import T from "prop-types";
import h from "@macrostrat/hyper";

interface FrameRegistry {
  [key: string]: ReactNode;
}
interface FrameCtx {
  //register(key: string, el: ReactNode): void
  registry: FrameRegistry;
  getElement(key: string): any;
}

const defaultCtx = {
  //register(k, el) { },
  registry: {},
  getElement(k) {
    return null;
  },
};
export const FrameContext = createContext<FrameCtx>(defaultCtx);

// custom hook to retrieve data from FrameContext

function FrameProvider({ overrides = {}, children }) {
  // could eventually create a registry state and register function
  return h(
    FrameContext.Provider,
    {
      value: {
        getElement(id) {
          return overrides[id] || null;
        },
        registry: overrides,
      },
    },
    children
  );
}

function useFrameOverride(id) {
  const { getElement } = useContext(FrameContext);
  return getElement(id);
}

const Frame = (props) => {
  /* Main component for overriding parts of the UI with
     lab-specific components. Must be nested below a *FrameProvider*
  */
  const { id, iface, children, ...rest } = props;
  const el = useFrameOverride(id);

  // By default we just render the children
  const defaultContent = children;
  let child = defaultContent;
  if (el != null) {
    // We have an override
    child = el;
  }

  // This is kinda sketchy for react component detection.
  if (typeof child === "function") {
    child = child({ ...rest, defaultContent });
  }

  return h(ErrorBoundary, null, child);
};

Frame.propTypes = {
  id: T.string.isRequired,
  iface: T.object,
  children: T.node,
  rest: T.object,
};

export { FrameProvider, Frame, useFrameOverride };
