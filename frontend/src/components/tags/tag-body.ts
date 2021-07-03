import { hyperStyled } from "@macrostrat/hyper";
import { Tooltip, Button } from "@blueprintjs/core";
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
  const {
    name,
    description,
    color,
    onClickDelete,
    isEditing = false,
    id = 10000,
    disabled = false,
  } = props;

  const showName = name.length > 0 ? name : "Tag Preview";
  const darkTag = isTooDark(color);

  const textColor = darkTag ? "white" : "black";

  console.log(isEditing);

  return h(Tooltip, { content: description, disabled }, [
    h(
      "div.tag-body",
      { key: id, style: { backgroundColor: color, color: textColor } },
      [showName, h.if(isEditing)(TagDeleteButton, { onClickDelete, id })]
    ),
  ]);
}

function TagDeleteButton(props) {
  const { onClickDelete, id } = props;

  return h(Button, {
    icon: "trash",
    minimal: true,
    intent: "danger",
    onClick: () => onClickDelete(id),
  });
}

export { TagBody };
