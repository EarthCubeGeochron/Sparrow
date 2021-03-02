import { Popover, Button } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { DataFileAdminPage } from "~/admin/data-file";
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

  return h(
    "div",
    { id, onDragStart: dragStart, onDragOver: dragOver, draggable },
    [childern]
  );
}
