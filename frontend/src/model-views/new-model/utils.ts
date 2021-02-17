import { hyperStyled } from "@macrostrat/hyper";
import { useReducer, useState, useContext } from "react";
import { Button, Drawer, Tooltip } from "@blueprintjs/core";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function FormSlider(props) {
  const { content, onClose = () => {}, model } = props;
  const [isOpen, setOpen] = useState(false);

  const changeOpen = () => {
    setOpen(!isOpen);
  };

  const close = () => {
    changeOpen();
    onClose();
  };

  return h("div", [
    h(Tooltip, { content: `Create new ${model}` }, [
      h(Button, {
        onClick: changeOpen,
        minimal: true,
        icon: "plus",
        intent: "success",
      }),
    ]),
    h(
      Drawer,
      {
        title: `Add a new ${model}`,
        isOpen,
        onClose: close,
        isCloseButtonShown: true,
      },
      [content, h(Button, { onClick: close, intent: "danger" }, ["Cancel"])]
    ),
  ]);
}
