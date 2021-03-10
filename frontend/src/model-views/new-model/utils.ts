import { hyperStyled } from "@macrostrat/hyper";
import { useReducer, useState, useContext } from "react";
import { Button, Drawer, Card } from "@blueprintjs/core";
import { useAPIActions } from "@macrostrat/ui-components";
import { APIV2Context } from "~/api-v2";
import styles from "./module.styl";

const h = hyperStyled(styles);

export async function getfunc(props) {
  const { url, params } = props;
  const { get } = useAPIActions(APIV2Context);
  try {
    const data = await get(url, params, {});
  } catch (error) {
    console.log(error);
  }
}

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
    h(Card, [
      h(
        Button,
        {
          onClick: changeOpen,
          minimal: true,
          icon: "plus",
          intent: "success",
        },
        [`Create a New ${model}`]
      ),
    ]),
    h(
      Drawer,
      {
        usePortal: true,
        className: "drawer-add",
        title: `Add a new ${model}`,
        isOpen,
        onClose: close,
        isCloseButtonShown: true,
      },
      [content, h(Button, { onClick: close, intent: "danger" }, ["Cancel"])]
    ),
  ]);
}

function isLetter(char) {
  if (char.toUpperCase() != char.toLowerCase()) {
    return true;
  } else {
    return false;
  }
}

export const isTitle = (search) => {
  let i = 0;
  for (let char of search) {
    if (isLetter(char)) {
      i += 1;
    }
  }
  if (i / search.length > 0.7) {
    return true;
  } else {
    return false;
  }
};
