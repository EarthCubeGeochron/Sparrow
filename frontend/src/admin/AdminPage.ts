import React, { useState, useRef } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Icon, Button } from "@blueprintjs/core";
import { getQueryString } from "@macrostrat/ui-components";
import classNames from "classnames";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function AdminPage(props) {
  const { listComponent, mainPageComponent } = props;
  const [hidden, setHidden] = useState(false);

  const className = classNames({ hidden });

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
    h("div.left-panel", { className }, [listComponent]),
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
