import { hyperStyled } from "@macrostrat/hyper";
import { Tooltip, Button, Tag } from "@blueprintjs/core";
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
    disabled = false
  } = props;

  const showName = name.length > 0 ? name : "Tag Preview";
  const darkTag = isTooDark(color);

  const textColor = darkTag ? "white" : "black";

  const onRemove = () => {
    onClickDelete(id);
  };

  return h(Tooltip, { content: description, disabled }, [
    h(
      Tag,
      {
        key: id,
        large: true,
        round: true,
        onRemove: isEditing && onRemove,
        style: { backgroundColor: color, color: textColor }
      },
      [showName]
    )
  ]);
}

export { TagBody };
