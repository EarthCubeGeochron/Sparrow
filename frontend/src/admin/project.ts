import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { useState } from "react";
import { Button, Icon, NonIdealState } from "@blueprintjs/core";
import { ProjectMatch } from "~/model-views/project";
import { ProjectListComponent } from "./infinite-scroll";
import styles from "./module.styl";
import { NoStateAdmin } from "./baseview";
import { AdminPage } from "./AdminPage";
import { AdminFilter } from "../filter";

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
      render: () => h(NoStateAdmin, { name: "Project" }),
    }),
  ]);
}

export function ProjectAdminPage() {
  const [params, setParams] = useState({});
  const possibleFilters = ["embargo", "location", "doi_like", "date_range"];

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
      listComponent: h(ProjectListComponent, { params }),
      possibleFilters,
      createParams,
    }),
    mainPageComponent: h(ProjectMainPanel),
  });
}
