import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";

import { ProjectMatch } from "~/model-views/project";
import { ProjectListComponent } from "./infinite-scroll";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function ProjectMainPanel() {
  const base = "/admin/project";
  return h(Switch, [
    h(
      Route,
      {
        path: base + "/:id",
      },
      h(ProjectMatch)
    ),
    h(Route, {
      path: base,
      component: () => h("div"),
    }),
  ]);
}

export function ProjectAdminPage() {
  return h("div.admin-page-main", [
    h("div.left-panel", [h(ProjectListComponent)]),
    h("div.right-panel", [h(ProjectMainPanel)]),
  ]);
}
