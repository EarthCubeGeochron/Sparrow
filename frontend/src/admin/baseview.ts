import React from "react";
import { hyperStyled } from "@macrostrat/hyper";
import styles from "./module.styl";
import { Icon, NonIdealState } from "@blueprintjs/core";

const h = hyperStyled(styles);

export const AnimatedArrow = () => {
  return h("div.animatedarrow", [
    h(Icon, { icon: "arrow-left", iconSize: 70 }),
  ]);
};

export function NoStateAdmin(props) {
  const { name } = props;

  const description =
    "Click one of the Links to the Left to view one of the Pages";

  const title = `No ${name} page selected`;

  return h("div.nostate", [
    h("div", { style: { paddingBottom: "50px", paddingTop: "100px" } }, [
      h(AnimatedArrow),
    ]),
    h("div", { style: { paddingTop: "50px", paddingBottom: "100px" } }, [
      h(NonIdealState, { title, description }),
    ]),
    h("div", { stlye: { paddingTop: "50px" } }, [h(AnimatedArrow)]),
  ]);
}
