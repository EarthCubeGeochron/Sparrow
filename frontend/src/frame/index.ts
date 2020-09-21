/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS206: Consider reworking classes to avoid initClass
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import { StatefulComponent } from "@macrostrat/ui-components";
import {
  Component,
  createContext,
  useContext,
  useState,
  Children,
} from "react";
import { ErrorBoundary } from "../util";
import T from "prop-types";
import h from "react-hyperscript";

export const FrameContext = createContext({});

// custom hook to retrieve data from FrameContext

// function FrameProvider({ props }) {
//   const { overrides, ...rest } = props;
//   const [state, setState] = useState({ registry: {} });
//   const getElement = (id) => {
//     return overrides[id] || null;
//   };
//   const register = (registry) => {
//     setState({ registry: registry });
//   };
//   const value = { register: register, getElement };
//   return h(FrameContext.Provider, { value }, props.children);
// }
class FrameProvider extends Component {
  static propTypes = {
    overrides: T.objectOf(T.node),
  };
  static defaultProps = { overrides: {} };
  constructor(props) {
    super(props);
    this.getElement = this.getElement.bind(this);
    this.state = { registry: {} };
  }
  render() {
    const value = { register: this.register, getElement: this.getElement };
    return h(FrameContext.Provider, { value }, this.props.children);
  }

  getElement(id) {
    const { overrides } = this.props;
    return overrides[id] || null;
  }
}

const Frame = (props) => {
  /* Main component for overriding parts of the UI with
     lab-specific components. Must be nested below a *FrameProvider*
  */
  const { getElement } = useContext(FrameContext);
  const { id, iface, children, ...rest } = props;
  const el = getElement(id);

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

export { FrameProvider, Frame };
