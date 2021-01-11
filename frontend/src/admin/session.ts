import { useState } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { NoStateAdmin } from "./baseview";
import { ProjectMatch } from "~/model-views/project";
import { SessionMatch } from "../model-views";
import { SessionListComponent } from "./infinite-scroll";
import { AdminPage } from "./AdminPage";
import { AdminFilter } from "../filter";
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
      render: () => h(NoStateAdmin, { name: "Session" }),
    }),
  ]);
}

export function SessionAdminPage() {
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
      listComponent: h(SessionListComponent, { params }),
      possibleFilters,
      createParams,
    }),
    mainPageComponent: h(SessionMainPanel),
  });
}
