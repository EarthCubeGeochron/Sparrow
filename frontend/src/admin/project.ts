import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { useState, createContext } from "react";
import { ProjectMatch } from "~/model-views/project";
import { ProjectListComponent } from "./infinite-scroll";
import styles from "./module.styl";
import { NoStateAdmin } from "./baseview";
import { AdminPage, createParamsFromURL } from "./AdminPage";
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

export const ProjectAdminContext = createContext({});



export function ProjectAdminPage() {
  const possibleFilters = ["public", "geometry", "doi_like", "date_range"];

  const [listName, setListName] = useState("list");

  const initialState = createParamsFromURL(possibleFilters);

  const [params, setParams] = useState(initialState);

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
      initParams: params || {},
    }),
    mainPageComponent: h(ProjectMainPanel),
  });
}
