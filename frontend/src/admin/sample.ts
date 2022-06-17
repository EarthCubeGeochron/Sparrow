import { useState, useContext, createContext, useEffect } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route, Link } from "react-router-dom";
import { NoStateAdmin } from "./baseview";
import { SampleMatch } from "~/model-views/sample";
import { SampleListComponent } from "~/model-views";
import { AdminPage, createParamsFromURL } from "./AdminPage";
import { AdminFilter } from "../filter";
import { ModelFilterLists, SampleFilterList } from "../model-views";
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

function SampleAdminList() {
  const { listName, updateFunction } = useContext(SampleAdminContext);
  return h("div", [
    h.if(listName == "main")(SampleFilterList, { link: true }),
    h.if(listName !== "main")(ModelFilterLists, {
      listName,
      onClick: updateFunction,
    }),
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
