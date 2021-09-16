import h from "@macrostrat/hyper";
import { Route, Switch, useRouteMatch } from "react-router-dom";
import { SamplePage } from "./page";
import { SampleList } from "./list";

function SampleMatch({ Edit = false }) {
  const id = useRouteMatch()?.params?.id;
  return h(SamplePage, { id, Edit });
}

function SampleMain(props) {
  const base = "/catalog/sample";
  // Render main body
  return h(Switch, [
    h(Route, {
      path: base + "/:id",
      component: SampleMatch,
    }),
    h(Route, {
      path: base,
      exact: true,
      component: SampleList,
    }),
  ]);
}

export { SampleMain, SamplePage, SampleList, SampleMatch };
