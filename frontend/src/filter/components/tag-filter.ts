import { TagContainer } from "~/model-views";
import { hyperStyled } from "@macrostrat/hyper";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

// interface tagContainer {
//   tags: tagBody[];
//   isEditing: boolean;
//   onChange: (e) => void;
//   onClickDelete: (e) => void;
//   modelName: string;
// }
export function TagFilter(props) {
  const { updateParams } = props;
  const onAdd = () => {};
  const onDelete = () => {};
  return h(TagContainer, {
    isEditing: true,
    onChange: onAdd,
    onClickDelete: onDelete,
    modelName: "filter"
  });
}
