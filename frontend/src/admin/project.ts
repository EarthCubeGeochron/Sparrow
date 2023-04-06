import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route, Link } from "react-router-dom";
import { useState, createContext, useContext, useEffect } from "react";
//@ts-ignore
import styles from "./module.styl";
import { NoStateAdmin } from "./baseview";
import { AdminPage, createParamsFromURL } from "./AdminPage";
import {
  ProjectMatch,
  ProjectListComponent,
  ModelFilterLists,
  ProjectFilterList,
} from "~/model-views";
import { NewProjectForm } from "../model-views/project/new-project";

const h = hyperStyled(styles);

function ProjectNoStateAdmin() {
  const { setListName } = useContext(ProjectAdminContext);
  const content = h("h3", [
    "Or create a new project",
    h(Link, { to: "/admin/project/new" }, [" here."]),
  ]);

  useEffect(() => {
    setListName("main");
  }, []);

  return h(NoStateAdmin, { name: "Project", content });
}

export function ProjectMainPanel() {
  const base = "/admin/project";
  const Edit = true;
  return h(Switch, [
    h(Route, {
      path: base + "/new",
      render: () => h(NewProjectForm),
    }),
    h(Route, {
      path: base + "/:id",
      render: () => h(ProjectMatch, { Edit }),
    }),
    h(Route, {
      path: base,
      render: () => h(ProjectNoStateAdmin, { name: "Project" }),
    }),
  ]);
}

export const ProjectAdminContext = createContext({});

const ProjectAdminList = (props) => {
  const { listName, updateFunction } = useContext(ProjectAdminContext);

  return h("div", [
    h.if(listName == "main")(ProjectFilterList, {
      link: true,
      onClick: undefined,
    }),
    h.if(listName !== "main")(ModelFilterLists, {
      onClick: updateFunction,
      listName,
    }),
  ]);
};

export function ProjectAdminPage() {
  const [listName, setListName] = useState("main");

  const [updateFunction, setUpdateFunction] = useState(() => {});

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
