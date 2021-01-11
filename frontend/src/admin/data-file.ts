import { useState } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { DataFileMatch } from "../model-views/data-files/page";
import { NoStateAdmin } from "./baseview";
import { AdminPage } from "./AdminPage";
import { AdminFilter } from "../filter";
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
  const [params, setParams] = useState({});
  const possibleFilters = ["embargo", "date_range"];

  const createParams = (params) => {
    for (let [key, value] of Object.entries(params)) {
      if (value == null) {
        delete params[key];
      }
    }
    setParams(params);
  };

  return h(AdminPage, {
    listComponent: h(AdminFilter, {
      listComponent: h(DataFilesListComponent, { params }),
      possibleFilters,
      createParams,
    }),
    mainPageComponent: h(DataFilesMainPanel),
  });
}
