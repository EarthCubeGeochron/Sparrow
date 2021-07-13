import { Card, Button } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";
import { hyperStyled } from "@macrostrat/hyper";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const ModelLinkCard = (props) => {
  /** A model link card for administration pages */
  const {
    minimal = true,
    className,
    to,
    link,
    indirect = false,
    linkedThrough = "",
    isEditing = false,
    children,
    onMouseEnter,
    onMouseLeave,
    draggable = false,
    styles = {},
    onClick,
  } = props;

  const component = link && !isEditing ? LinkCard : Card;

  const cardClassName = indirect ? "indirect-link" : "sample-card";

  if (isEditing) {
    return h(
      component,
      {
        className: cardClassName,
        to,
        onMouseEnter,
        onMouseLeave,
        draggable,
        style: { position: "relative", ...styles },
      },
      [
        h(Button, {
          style: {
            position: "absolute",
            top: "0",
            right: "0",
            marginLeft: "5px",
          },
          icon: "small-cross",
          minimal: true,
          intent: "danger",
          onClick,
        }),
        h("div", [children]),
      ]
    );
  }

  return h("div", [
    h(
      component,
      {
        className: cardClassName,
        to,
        onMouseEnter,
        onMouseLeave,
        draggable,
        style: { ...styles },
      },
      [children]
    ),
    h.if(indirect)(
      "div",
      { style: { fontSize: "10px", marginLeft: "10px", fontStyle: "italic" } },
      ["Linked through ", linkedThrough]
    ),
  ]);
};
