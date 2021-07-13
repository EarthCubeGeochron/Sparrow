import { Tooltip, Card, Button } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";
import { format } from "date-fns";
import { useModelURL } from "~/util";
import { hyperStyled } from "@macrostrat/hyper";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const AddCard = (props) => {
  const { onClick, model } = props;
  return h(
    Tooltip,
    { content: `Select from exisitng ${model}s` },
    h(Button, { onClick, icon: "small-plus", minimal: true })
  );
};

export const NewModelButton = (props) => {
  const { model } = props;

  const to = useModelURL(`/${model}/new`);
  const handleClick = (e) => {
    e.preventDefault();
    window.location.href = to;
  };

  const string = model.charAt(0).toUpperCase() + model.slice(1);

  return h(
    Button,
    {
      minimal: true,
      intent: "success",
      onClick: handleClick,
    },
    [`New ${string}`]
  );
};

export const ModelAttributeOneLiner = (props) => {
  const { title, content } = props;

  let displayContent;
  if (!content) {
    displayContent = "None";
  } else {
    displayContent = content;
  }

  return h("span", { style: { display: "flex", alignItems: "baseline" } }, [
    h("h4", { style: { marginRight: "4px" } }, title),
    " ",
    displayContent,
  ]);
};

export const ModelLinkCard = (props) => {
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
