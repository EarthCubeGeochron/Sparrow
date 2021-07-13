import { Card, Button } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";
import { hyperStyled } from "@macrostrat/hyper";
import classNames from "classnames";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

function RemoveButton({ onClick }) {
  return h(Button, {
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
  });
}

export const ModelLinkCard = (props) => {
  /** A model link card for administration pages */
  const {
    minimal = true,
    className,
    to,
    link,
    indirect = false,
    linkedThrough,
    isEditing = false,
    children,
    onMouseEnter,
    onMouseLeave,
    draggable = false,
    styles = {},
    onClick,
  } = props;

  const component = link && !isEditing ? LinkCard : Card;

  return h("div.model-link-container", [
    h(
      component,
      {
        className: classNames(
          { "indirect-link": indirect },
          "model-card",
          className
        ),
        to,
        onMouseEnter,
        onMouseLeave,
        draggable,
        style: { position: "relative", ...styles },
      },
      [
        h.if(isEditing && linkedThrough == null)(RemoveButton, {
          onClick,
        }),
        children,
      ]
    ),
    h.if(linkedThrough != null)("div.model-card-link", [
      "Linked through ",
      linkedThrough,
    ]),
  ]);
};
