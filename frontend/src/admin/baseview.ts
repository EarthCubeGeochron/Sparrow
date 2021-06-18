import { hyperStyled } from "@macrostrat/hyper";
import styles from "./module.styl";
import { Icon, NonIdealState } from "@blueprintjs/core";

const h = hyperStyled(styles);

export const AnimatedArrow = () => {
  return h("div.animatedarrow", [
    h(Icon, { icon: "arrow-left", iconSize: 70 })
  ]);
};
/**
 * @description Default page when nothing selected on left navigation
 */
export function NoStateAdmin(props) {
  const { name, content = null } = props;

  const description =
    "Click one of the Links to the Left to view one of the Pages";

  const title = `No ${name} page selected`;

  return h(NonIdealState, { title, description, icon: "hand-left" }, [content]);
}
