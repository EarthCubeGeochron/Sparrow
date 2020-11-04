import React, { useState } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Icon, Button } from "@blueprintjs/core";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function AdminPage(props) {
  const { ListComponent, MainPageComponent } = props;
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
    h(`div.${classname}`, null, [ListComponent]),
    h("div.right-panel", null, [MainPageComponent]),
  ]);
}
