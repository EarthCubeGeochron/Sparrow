import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { DataFileMatch } from "../model-views/data-files/page";
import { NoStateAdmin } from "./baseview";
import { AdminPage } from "./AdminPage";
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
      component: () => h(NoStateAdmin, { name: "Data File" }),
    }),
  ]);
}

export function DataFileAdminPage() {
  return h(AdminPage, {
    listComponent: h(DataFilesListComponent),
    mainPageComponent: h(DataFilesMainPanel),
  });
}
