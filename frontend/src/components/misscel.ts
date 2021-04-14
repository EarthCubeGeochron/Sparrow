import { useState } from "react";
import { Popover, Button, Switch } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function HelpButton(props) {
  const { content, position = "bottom-right" } = props;
  return h(
    Popover,
    {
      content,
      minimal: true,
      position,
      modifiers: {
        preventOverflow: { enabled: false },
        flip: { enabled: true },
        hide: { enabled: false },
      },
    },
    [h(Button, { minimal: true, intent: "danger" }, ["Help"])]
  );
}

export function DndContainer(props) {
  const {
    children,
    onDrop = (data) => console.log(data),
    id,
    data_id = "child_id",
  } = props;

  const drop = (e) => {
    e.preventDefault();
    const child = JSON.parse(e.dataTransfer.getData(data_id));

    //console.log(child);
    onDrop(child, id);
  };

  const dragOver = (e) => {
    e.preventDefault();
  };

  return h("div", { id, onDrop: drop, onDragOver: dragOver }, [children]);
}

export function DndChild(props) {
  const { childern, id, data, draggable = true, data_id = "child_id" } = props;

  const dragStart = (e) => {
    const target = e.target;
    //console.log(data);
    const d = JSON.stringify(data);
    e.dataTransfer.setData(data_id, d);
  };

  const dragOver = (e) => {
    e.stopPropagation();
  };

  const dragProps = draggable
    ? { id, onDragStart: dragStart, onDragOver: dragOver, draggable }
    : {};

  return h("div", { ...dragProps }, [childern]);
}

export function MySwitch(props) {
  const { checked, onChange } = props;
  return h(Switch, { checked, onChange });
}

export function useToggle(initialValue: boolean): [boolean, () => void] {
  const [value, setValue] = useState<boolean>(initialValue);
  const toggleValue = () => setValue(!value);
  return [value, toggleValue];
}

export const randomHexColor = () => {
  const hexColor = "#" + Math.floor(Math.random() * 16777215).toString(16);
  return hexColor;
};

/**
 * This function parses a hexcode and decides if the color is dark
 * @param hexcolor : string, hex code for color
 * @returns boolean (true == dark)
 */
export function isTooDark(hexcolor) {
  var r = parseInt(hexcolor.substr(1, 2), 16);
  var g = parseInt(hexcolor.substr(3, 2), 16);
  var b = parseInt(hexcolor.substr(4, 2), 16);
  var yiq = (r * 299 + g * 587 + b * 114) / 1000;

  return yiq < 90;
}
