import React from "react";
import { Callout } from "@blueprintjs/core";
import { Route } from "react-router-dom";
import h from "@macrostrat/hyper";

function ErrorCallout(props) {
  const { error, description, title } = props;

  const des = description ? description : error.toString();

  return h(
    Callout,
    {
      title,
      icon: "error",
      intent: "danger",
    },
    [h("p", [des])]
  );
}

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { error };
  }

  componentDidCatch(error, info) {
    // You can also log the error to an error reporting service
    console.log(error);
  }

  render() {
    if (this.state.error != null) {
      let { description } = this.props;
      const { error } = this.state;
      if (description == null) description = error.toString();
      // You can render any custom fallback UI
      return h(ErrorCallout, {
        error,
        description,
        title: "A rendering error has occured",
      });
    }

    return this.props.children;
  }
}

const ErrorBoundaryRoute = function(props) {
  const { component, render: baseRender, ...rest } = props;

  // Use render function unless component is provided
  let render = baseRender;
  if (component != null) {
    render = () => h(component);
  }

  return h(Route, {
    ...rest,
    render() {
      return h(ErrorBoundary, null, render());
    },
  });
};

export { ErrorBoundaryRoute, ErrorBoundary, ErrorCallout };
