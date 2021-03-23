import { useState, useContext, createContext } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { NoStateAdmin } from "./baseview";
import { SampleMatch } from "~/model-views/sample/list";
import { SampleListComponent } from "../components/infinite-scroll/infinite-scroll";
import { AdminPage, createParamsFromURL } from "./AdminPage";
import { AdminFilter } from "../filter";
import { ProjectFilterList, SessionFilterList } from "../model-views/components/new-model";
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
  ]);
}

export function SampleAdminPage() {
  const [listName, setListName] = useState("main");

  const [updateFunction, setUpdateFunction] = useState(() =>
    console.log("add")
  );

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
