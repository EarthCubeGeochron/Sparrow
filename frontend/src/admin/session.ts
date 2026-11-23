import { useState, createContext, useContext } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { NoStateAdmin } from "./baseview";
import {
  ModelFilterLists,
  SessionFilterList,
  SessionMatch,
} from "../model-views";
import { SessionListComponent } from "~/model-views";
import { AdminPage, createParamsFromURL } from "./AdminPage";
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

export const SessionAdminContext = createContext({});

function SessionAdminList() {
  const { listName, updateFunction } = useContext(SessionAdminContext);

  return h("div", [
    h.if(listName == "main")(SessionFilterList, { link: true }),
    h.if(listName !== "main")(ModelFilterLists, {
      onClick: updateFunction,
      listName,
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
