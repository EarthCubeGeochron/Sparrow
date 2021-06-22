import { Tooltip, Card, Button } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";

import { hyperStyled } from "@macrostrat/hyper";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const AddCard = props => {
  const { onClick, model } = props;
  return h(
    Tooltip,
    { content: `Select from exisitng ${model}s` },
    h(Button, { onClick, icon: "small-plus", minimal: true })
  );
};

export const ModelAttributeOneLiner = props => {
  return h("span", { style: { display: "flex", alignItems: "baseline" } }, [
    h("h4", { style: { marginRight: "4px" } }, props.title),
    " ",
    h("div", props.content)
  ]);
};

export const PageViewBlock = props => {
  const {
    elevation = 1,
    title,
    children,
    isEditing = false,
    modelLink = false,
    onClick = () => {},
    hasData = true,
    model = "model"
  } = props;

  if (modelLink) {
    return h(Card, { elevation, style: { marginBottom: "15px" } }, [
      h("div", { style: { display: "flex", alignItems: "baseline" } }, [
        h("h3", [title]),
        h.if(isEditing)(AddCard, { onClick, model })
      ]),
      h.if(!hasData)("h4", `No ${model}s`),
      children
    ]);
  }

  return h(Card, { elevation, style: { marginBottom: "15px" } }, [
    h("h2", [title]),
    h.if(!hasData)("h4", `No ${model}s`),
    children
  ]);
};

export const PageViewModelCard = props => {
  const {
    minimal = true,
    className,
    to,
    link,
    isEditing = false,
    children,
    onMouseEnter,
    onMouseLeave,
    draggable = false,
    styles = {},
    onClick
  } = props;

  const component = link && !isEditing ? LinkCard : Card;

  if (isEditing) {
    return h(
      component,
      {
        className: "sample-card",
        to,
        onMouseEnter,
        onMouseLeave,
        draggable,
        style: { ...styles }
      },
      [
        h("div", { style: { display: "flex" } }, [
          h("div", [children]),
          h(Button, {
            icon: "small-cross",
            minimal: true,
            intent: "danger",
            onClick
          })
        ])
      ]
    );
  }

  return h(
    component,
    {
      className: "sample-card",
      to,
      onMouseEnter,
      onMouseLeave,
      draggable,
      style: { ...styles }
    },
    [children]
  );
};
