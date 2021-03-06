import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { DataFileMatch } from "../model-views/data-files/page";

import { DataFilesListComponent } from "./infinite-scroll";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function DataFilesMainPanel() {
  const base = "/admin/data-file";
  return h(Switch, [
    h(Route, {
      path: base + "/:file_hash",
      component: () => h(DataFileMatch),
    }),
    h(Route, {
      path: base,
      component: () => h("div"),
    }),
  ]);
}

export function DataFileAdminPage() {
  return h("div.admin-page-main", [
    h("div.left-panel", [h(DataFilesListComponent)]),
    h("div.right-panel", [h(DataFilesMainPanel)]),
  ]);
}
