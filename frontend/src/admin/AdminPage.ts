import { useState } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Icon, Button } from "@blueprintjs/core";
import styles from "./module.styl";
import classNames from "classnames";

const h = hyperStyled(styles);

const SidebarButton = ({ hidden, setHidden }) => {
  const handleClick = () => {
    setHidden(!hidden);
  };
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
          hidden ? "Expand" : "Hide",
          h("br"),
          h(Icon, { icon: hidden ? "arrow-up" : "arrow-down" }),
        ]),
      ]
    ),
  ]);
};

export function AdminPage(props) {
  const { ListComponent, MainPageComponent } = props;
  const [hidden, setHidden] = useState(false);

  const className = classNames({ hidden });

  return h("div.admin-page-main", [
    h(SidebarButton, { hidden, setHidden }),
    h("div.left-panel", { className }, [ListComponent]),
    h("div.right-panel", null, [MainPageComponent]),
  ]);
}
