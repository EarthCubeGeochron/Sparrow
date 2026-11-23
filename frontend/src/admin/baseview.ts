import { hyperStyled } from "@macrostrat/hyper";
import styles from "./module.styl";
import { Icon, NonIdealState } from "@blueprintjs/core";

const h = hyperStyled(styles);

export const AnimatedArrow = () => {
  return h("div.animatedarrow", [
    h(Icon, { icon: "arrow-left", iconSize: 70 }),
  ]);
};
/**
 * @description Default page when nothing selected on left navigation
 */
export function NoStateAdmin(props) {
  const { name, content = null, children } = props;

  const description = "Use the left panel to select a model.";
  const title = `No ${name} selected`;
  return h(
    NonIdealState,
    { title, description, icon: "inbox" },
    children ?? content
  );
}
