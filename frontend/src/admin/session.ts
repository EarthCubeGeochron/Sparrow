import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";

import { ProjectMatch } from "~/model-views/project";
import { SessionMatch } from "../model-views";
import { SessionListComponent } from "./infinite-scroll";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function SessionMainPanel() {
  const base = "/admin/session";
  return h(Switch, [
    h(
      Route,
      {
        path: base + "/:id",
      },
      h(SessionMatch)
    ),
    h(Route, {
      path: base,
      component: () => h("div"),
    }),
  ]);
}

export function SessionAdminPage() {
  return h("div.admin-page-main", [
    h("div.left-panel", [h(SessionListComponent)]),
    h("div.right-panel", [h(SessionMainPanel)]),
  ]);
}
