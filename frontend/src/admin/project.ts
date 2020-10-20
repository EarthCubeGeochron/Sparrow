import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";

import { ProjectMatch } from "~/model-views/project";
import { ProjectListComponent } from "./infinite-scroll";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function ProjectMainPanel() {
  const base = "/admin/project";
  const Edit = true;
  return h(Switch, [
    h(Route, {
      path: base + "/:id",
      render: () => h(ProjectMatch, { Edit }),
    }),
    h(Route, {
      path: base,
      render: () => h("div"),
    }),
  ]);
}

export function ProjectAdminPage() {
  return h("div.admin-page-main", [
    h("div.left-panel", null, h(ProjectListComponent)),
    h("div.right-panel", null, h(ProjectMainPanel)),
  ]);
}
