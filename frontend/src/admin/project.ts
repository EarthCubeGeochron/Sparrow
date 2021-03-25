import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { useState, createContext, useContext } from "react";
import { ProjectMatch } from "~/model-views/project";
import { ProjectListComponent } from "../components/infinite-scroll/infinite-scroll";
//@ts-ignore
import styles from "./module.styl";
import { NoStateAdmin } from "./baseview";
import { AdminPage, createParamsFromURL } from "./AdminPage";
import {
  SampleFilterList,
  PublicationFilterList,
  ResearcherFilterList,
  SessionFilterList,
} from "~/model-views/components/new-model";
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

const mainFilterList = (props) => {
  const possibleFilters = ["public", "geometry", "doi_like", "date_range"];

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

  return h(AdminFilter, {
    listComponent: h(ProjectListComponent, { params }),
    possibleFilters,
    createParams,
    initParams: params || {},
  });
};

const ProjectAdminList = (props) => {
  const { listName, updateFunction } = useContext(ProjectAdminContext);

  return h("div", [
    h.if(listName == "main")(mainFilterList),
    h.if(listName == "sample")(SampleFilterList, {
      onClick: updateFunction,
    }),
    h.if(listName == "publication")(PublicationFilterList, {
      onClick: updateFunction,
    }),
    h.if(listName == "researcher")(ResearcherFilterList, {
      onClick: updateFunction,
    }),
    h.if(listName == "session")(SessionFilterList, {
      onClick: updateFunction,
    }),
  ]);
};

export function ProjectAdminPage() {
  const [listName, setListName] = useState("main");

  const [updateFunction, setUpdateFunction] = useState(() =>
    console.log("add")
  );

  const changeFunction = (func) => {
    setUpdateFunction(() => func);
  };

  return h(
    ProjectAdminContext.Provider,
    { value: { setListName, updateFunction, listName, changeFunction } },
    [
      h(AdminPage, {
        listComponent: h(ProjectAdminList),
        mainPageComponent: h(ProjectMainPanel),
      }),
    ]
  );
}
