import { Component } from "react";
import h from "@macrostrat/hyper";
import { Route, Switch } from "react-router-dom";
import { SamplePage } from "./page";
import { SampleComponent, SampleList, SampleMatch } from "./list";

function SampleMain(props) {
  const { match } = props;
  const base = "/catalog/sample";
  // Render main body
  return h(Switch, [
    h(
      Route,
      {
        path: base + "/:id",
      },
      [h(SampleMatch)]
    ),
    h(Route, {
      path: base,
      component: SampleList,
      exact: true,
    }),
  ]);
}

export { SampleMain, SamplePage, SampleList };
export * from "./detail-card";
