import h from "@macrostrat/hyper";
import { Route, Switch } from "react-router-dom";
import { SamplePage } from "./page";
import { SampleList, SampleMatch } from "./list";

function SampleMain(props) {
  const { match } = props;
  const base = match.path;
  // Render main body
  return h(Switch, [
    h(Route, {
      path: base + "/:id",
      component: SampleMatch,
    }),
    h(Route, {
      path: base,
      render() {
        return h(SampleList);
      },
      exact: true,
    }),
  ]);
}

export { SampleMain, SamplePage, SampleList };
export * from "./detail-card";
