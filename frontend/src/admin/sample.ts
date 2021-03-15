import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { NoStateAdmin } from "./baseview";
import { SampleMatch } from "~/model-views/sample/list";
import { SampleListComponent } from "./infinite-scroll";
import { AdminPage } from "./AdminPage";
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
  return h(AdminPage, {
    ListComponent: h(SampleListComponent),
    MainPageComponent: h(SampleMainPanel),
  });
}
