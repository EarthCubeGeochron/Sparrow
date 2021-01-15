import { useState } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { NoStateAdmin } from "./baseview";
import { SampleMatch } from "~/model-views/sample/list";
import { SampleListComponent } from "./infinite-scroll";
import { AdminPage } from "./AdminPage";
import { AdminFilter } from "../filter";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function SampleMainPanel() {
  const base = "/admin/sample";
  return h(Switch, [
    h(Route, {
      path: base + "/:id",
      render() {
        return h(SampleMatch, { Edit: true });
      },
    }),
    h(Route, {
      path: base,
      component: () => h(NoStateAdmin, { name: "Sample" }),
    }),
  ]);
}

export function SampleAdminPage() {
  const [params, setParams] = useState({});
  const possibleFilters = ["embargo", "location", "date_range"]; //needs to work with "doi_like"

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
      listComponent: h(SampleListComponent, { params }),
      possibleFilters,
      createParams,
    }),
    mainPageComponent: h(SampleMainPanel),
  });
}
