import { hyperStyled } from "@macrostrat/hyper";
import { Switch, Route } from "react-router-dom";
import { useState } from "react";
import { Button, Icon } from "@blueprintjs/core";
import { ProjectMatch } from "~/model-views/project";
import { ProjectListComponent } from "./infinite-scroll";
import styles from "./module.styl";

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
      render: () => h("div"),
    }),
  ]);
}

export function ProjectAdminPage() {
  const [hidden, setHidden] = useState(false);

  const classname = hidden ? "left-panel.hidden" : "left-panel";

  const SidebarButton = () => {
    const iconname = hidden ? "arrow-right" : "arrow-left";

    return h(
      Button,
      {
        onClick: () => setHidden(!hidden),
        minimal: true,
        //rightIcon: iconname,
      },
      [
        h("div", { style: { display: "flex", flexDirection: "column" } }, [
          h(Icon, {
            icon: iconname,
            style: { paddingBottom: "150px", paddingTop: "100px" },
          }),
          h(Icon, {
            icon: iconname,
            style: { paddingBottom: "150px" },
          }),
          h(Icon, {
            icon: iconname,
            style: { paddingBottom: "150px" },
          }),
          h(Icon, {
            icon: iconname,
            style: { paddingBottom: "150px" },
          }),
        ]),
      ]
    );
  };

  return h("div.admin-page-main", [
    h(SidebarButton),
    h(`div.${classname}`, null, [h(ProjectListComponent)]),
    h("div.right-panel", null, [h(ProjectMainPanel)]),
  ]);
}
