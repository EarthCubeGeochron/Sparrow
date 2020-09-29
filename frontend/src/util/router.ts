import h from "@macrostrat/hyper";
import { useLocation, Route } from "react-router-dom";
import { PageSkeleton, InsetText } from "~/components";

export const NoMatchPage = function () {
  let location = useLocation();
  return h(InsetText, [
    h("h2", "404"),
    h("h3", ["No match for ", h("code", location.pathname), "."]),
  ]);
};

export function PageRoute(props) {
  /** A custom route to manage page header, footer, and style associated
      with a specific route */
  const { render, component: base, style, ...rest } = props;
  const component = (p) => {
    const children = base != null ? h(base, p) : render(p);
    return h(PageSkeleton, { style, children });
  };
  return h(Route, { ...rest, component });
}
