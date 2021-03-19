import { AddSampleCard } from "../new-model/detail-card";
import { Tooltip } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const AddCard = (props) => {
  const { onClick, model } = props;
  return h(
    Tooltip,
    { content: `Select from exisitng ${model}s` },
    h(AddSampleCard, { onClick, icon_name: "plus" })
  );
};
