import { useState, createContext, useContext } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { NoStateAdmin } from "./baseview";
import { SessionMatch } from "../model-views";
import { SessionListComponent } from "./infinite-scroll";
import { AdminPage, createParamsFromURL } from "./AdminPage";
import { AdminFilter } from "../filter";
import {
  ProjectFilterList,
  PublicationFilterList,
  SampleFilterList,
} from "../model-views/new-model";
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

export const SessionAdminContext = createContext({});

const MainFilterList = () => {
  const possibleFilters = ["public", "date_range"];

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
    listComponent: h(SessionListComponent, { params }),
    possibleFilters,
    createParams,
    initParams: params || {},
  });
};

function SessionAdminList() {
  const { listName, updateFunction } = useContext(SessionAdminContext);

  return h("div", [
    h.if(listName == "main")(MainFilterList),
    h.if(listName == "project")(ProjectFilterList, { onClick: updateFunction }),
    h.if(listName == "sample")(SampleFilterList, { onClick: updateFunction }),
    h.if(listName == "publication")(PublicationFilterList, {
      onClick: updateFunction,
    }),
  ]);
}

export function SessionAdminPage() {
  const [listName, setListName] = useState("main");

  const [updateFunction, setUpdateFunction] = useState(() =>
    console.log("add")
  );

  const changeFunction = (func) => {
    setUpdateFunction(() => func);
  };

  return h(
    SessionAdminContext.Provider,
    { value: { setListName, updateFunction, listName, changeFunction } },
    [
      h(AdminPage, {
        listComponent: h(SessionAdminList),
        mainPageComponent: h(SessionMainPanel),
      }),
    ]
  );
}
