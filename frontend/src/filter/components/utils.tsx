import { useState, useEffect } from "react";
import { Collapse, Button, Icon } from "@blueprintjs/core";
import h from "@macrostrat/hyper";

export function FilterAccordian(props) {
  const { content, text, onOpen } = props;

  const [open, setOpen] = useState(false);

  const iconName = open ? "chevron-up" : "chevron-down";

  const handleClick = () => {
    setOpen(!open);
  };

  return h("div", [
    text,
    h(Button, { onClick: handleClick, icon: iconName, minimal: true }),
    h(Collapse, { isOpen: open }, [content]),
  ]);
}
