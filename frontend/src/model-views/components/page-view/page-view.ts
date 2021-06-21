import { AddSampleCard } from "../new-model/detail-card";
import { Tooltip } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const AddCard = props => {
  const { onClick, model } = props;
  return h(
    Tooltip,
    { content: `Select from exisitng ${model}s` },
    h(AddSampleCard, { onClick, icon_name: "plus" })
  );
};

export const ModelAttributeOneLiner = props => {
  return h("span", { style: { display: "flex", alignItems: "baseline" } }, [
    h("h4", { style: { marginRight: "4px" } }, props.title),
    " ",
    h("div", props.content)
  ]);
};