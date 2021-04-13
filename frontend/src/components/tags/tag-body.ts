import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { Tooltip2 } from "@blueprintjs/popover2";
//@ts-ignore
import styles from "./module.styl";
import { tagBody } from "./types";

const h = hyperStyled(styles);

/**
 *
 * @param props: tagBody
 * @returns
 */
function TagBody(props: tagBody) {
  const { name, description, color } = props;

  return h(Tooltip2, { content: description }, [
    h("div.tag-body", { style: { color } }, [name]),
  ]);
}

export { TagBody };
