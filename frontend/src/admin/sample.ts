import { useState, useContext, createContext, useEffect } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route, Link } from "react-router-dom";
import { NoStateAdmin } from "./baseview";
import { SampleMatch } from "~/model-views/sample/list";
import { SampleListComponent } from "~/model-views";
import { AdminPage, createParamsFromURL } from "./AdminPage";
import { AdminFilter } from "../filter";
import {
  ProjectFilterList,
  SessionFilterList,
  SampleFilterList
} from "../model-views/components/new-model";
import { NewSamplePage } from "~/model-views/sample/new-sample";

import styles from "./module.styl";

const h = hyperStyled(styles);

function SampleNoStateAdmin() {
  const { setListName } = useContext(SampleAdminContext);
  const content = h("h3", [
    "Or create a new sample",
    h(Link, { to: "/admin/sample/new" }, [" here."]),
  ]);

  useEffect(() => {
    setListName("main");
  }, []);

  return h(NoStateAdmin, { name: "Sample", content });
}

export function SampleMainPanel() {
  const base = "/admin/sample";
  return h(Switch, [
    h(Route, {
      path: base + "/new",
      render: () => h(NewSamplePage),
    }),
    h(Route, {
      path: base + "/:id",
      render() {
        return h(SampleMatch, { Edit: true });
      },
    }),
    h(Route, {
      path: base,
      component: () => h(SampleNoStateAdmin, { name: "Sample" }),
    }),
  ]);
}

export const SampleAdminContext = createContext({});

const MainFilterList = () => {
  const possibleFilters = ["public", "geometry", "date_range"]; //needs to work with "doi_like"

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
    listComponent: h(SampleListComponent, { params }),
    possibleFilters,
    createParams,
    initParams: params || {},
  });
};

function SampleAdminList() {
  const { listName, updateFunction } = useContext(SampleAdminContext);
  return h("div", [
    h.if(listName == "main")(MainFilterList),
    h.if(listName == "project")(ProjectFilterList, { onClick: updateFunction }),
    h.if(listName == "session")(SessionFilterList, { onClick: updateFunction }),
    h.if(listName == "sample")(SampleFilterList, { onClick: updateFunction })
  ]);
}

export function SampleAdminPage() {
  const [listName, setListName] = useState("main");

  const [updateFunction, setUpdateFunction] = useState(() => {});

  const changeFunction = (func) => {
    setUpdateFunction(() => func);
  };

  return h(
    SampleAdminContext.Provider,
    { value: { setListName, updateFunction, listName, changeFunction } },
    [
      h(AdminPage, {
        listComponent: h(SampleAdminList),
        mainPageComponent: h(SampleMainPanel),
      }),
    ]
  );
}
