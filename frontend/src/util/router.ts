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
  const { render: baseRender, component: base, style, ...rest } = props;
  const render = (p) => {
    // Choose between a component or render function
    const children = base != null ? h(base, p) : baseRender(p);
    return h(PageSkeleton, { style, children });
  };
  return h(Route, { ...rest, render });
}

export function useModelURL(tail) {
  const { pathname } = useLocation();
  const base = pathname.startsWith("/admin") ? "/admin" : "/catalog";
  return base + tail;
}

/**
 * returns true if on admin page
 */
export function useModelURLBool() {
  const { pathname } = useLocation();
  const onAdmin = pathname.startsWith("/admin");
  return onAdmin;
}
