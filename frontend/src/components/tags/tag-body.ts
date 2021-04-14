import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { Tooltip } from "@blueprintjs/core";
import { isTooDark } from "../misscel";
import { tagBody } from "./types";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

/**
 *
 * @param props: tagBody
 * @returns
 */
function TagBody(props: tagBody) {
  const { name, description, color, id = 10000 } = props;

  const showName = name.length > 0 ? name : "Tag Preview";
  const darkTag = isTooDark(color);

  const textColor = darkTag ? "white" : "black";

  return h(Tooltip, { content: description }, [
    h(
      "div.tag-body",
      { key: id, style: { backgroundColor: color, color: textColor } },
      [showName]
    ),
  ]);
}

export { TagBody };
