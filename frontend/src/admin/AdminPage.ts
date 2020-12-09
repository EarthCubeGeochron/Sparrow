import React, { useState, useRef } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Icon, Button } from "@blueprintjs/core";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function AdminPage(props) {
  const { listComponent, mainPageComponent } = props;
  const [hidden, setHidden] = useState(false);

  const classname = hidden ? "left-panel.hidden" : "left-panel";

  const handleClick = () => {
    setHidden(!hidden);
  };

  const SidebarButton = () => {
    const iconname = hidden ? "arrow-up" : "arrow-down";

    const text = hidden ? "Expand" : "Hide";

    return h("div", { style: { zIndex: 900 } }, [
      h(
        Button,
        {
          style: { width: "15px", height: "100px" },
          onClick: handleClick,
          minimal: true,
        },
        [
          h("div.vertical", { style: { display: "flex" } }, [
            text,
            h("br"),
            h(Icon, { icon: iconname }),
          ]),
        ]
      ),
    ]);
  };
  return h("div.admin-page-main", [
    h(SidebarButton),
    h(`div.${classname}`, null, [listComponent]),
    h("div.right-panel", null, [mainPageComponent]),
  ]);
}
