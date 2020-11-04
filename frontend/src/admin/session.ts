import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { NoStateAdmin } from "./baseview";
import { ProjectMatch } from "~/model-views/project";
import { SessionMatch } from "../model-views";
import { SessionListComponent } from "./infinite-scroll";
import { AdminPage } from "./AdminPage";
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
  return h(AdminPage, {
    ListComponent: h(SessionListComponent),
    MainPageComponent: h(SessionMainPanel),
  });
}
