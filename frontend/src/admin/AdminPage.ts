import React, { useState, useRef } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Icon, Button } from "@blueprintjs/core";
import { getQueryString } from "@macrostrat/ui-components";
import classNames from "classnames";
import styles from "./main.module.styl";

const h = hyperStyled(styles);

export function AdminPage(props) {
  const { listComponent, mainPageComponent } = props;
  const [hidden, setHidden] = useState(false);

  const className = classNames({ hidden });

  const handleClick = () => {
    setHidden(!hidden);
  };

  const SidebarButton = () => {
    const iconname = hidden ? "arrow-right" : "arrow-left";

    const text = hidden ? "Expand" : "Hide";

    return h("div.sidebar-toggle", [
      h(
        Button,
        {
          className: styles["sidebar-toggle-button"],
          onClick: handleClick,
          minimal: true,
          title: `${text} admin list`,
          "aria-controls": "admin-sidebar",
          "aria-expanded": !hidden,
        },
        [
          h("div.sidebar-toggle-label", [
            h("span", text),
            h(Icon, { icon: iconname }),
          ]),
        ]
      ),
    ]);
  };
  return h("div.admin-page-main", [
    h(SidebarButton),
    h("div.left-panel", { id: "admin-sidebar", className }, [listComponent]),
    h("div.right-panel", null, [mainPageComponent]),
  ]);
}

export function createParamsFromURL(possibleFilters) {
  if (!window.location.search) return;
  //console.log(getQueryString());
  const text = decodeURIComponent(window.location.search); // needs the decode so there isn't double serialization
  const tex = text.split("?");
  const te = tex[1].split("&");
  let paramList = {};
  for (let param of te) {
    let params = param.split("="); //params[0] is Key and params[1] is value
    let key1 = params[0];
    let value = params[1];
    paramList[key1] = value;
  }
  for (let key of Object.keys(paramList)) {
    if (!possibleFilters.includes(key)) {
      delete paramList[key];
    }
  }

  return paramList;
}
