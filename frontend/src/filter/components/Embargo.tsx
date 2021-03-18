import React, { useState } from "react";
import { Switch, Checkbox, Card, Button, ButtonGroup } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { FilterAccordian } from "./utils";
import styles from "./module.styl";

const h = hyperStyled(styles);
/**
 *
 * @param props function to update state of parent component, build get request params
 *
 * function to change
 */
export function EmabrgoSwitch(props) {
  const { updateEmbargoFilter } = props;
  const [clicked, setClicked] = useState("null");

  const handleClick = (state) => {
    updateEmbargoFilter("public", state);
    setClicked(JSON.stringify(state));
  };

  const intentFinder = (state) => {
    if (state == clicked) {
      return "success";
    }
    return null;
  };

  // Instead of switch three button group
  const Buttons = h(ButtonGroup, { minimal: true }, [
    h(
      "div",
      {
        style: {
          borderStyle: "solid",
          borderColor: "grey",
          borderRadius: "5px",
          borderWidth: "1px",
        },
      },
      [
        h(
          Button,
          {
            onClick: () => handleClick(null),
            intent: intentFinder("null"),
            active: clicked == "null",
          },
          ["Any"]
        ),
        h(
          Button,
          {
            onClick: () => handleClick(true),
            intent: intentFinder("true"),
            active: clicked == "true",
          },
          ["Public Only"]
        ),
        h(
          Button,
          {
            onClick: () => handleClick(false),
            intent: intentFinder("false"),
            active: clicked == "false",
          },
          ["Private Only"]
        ),
      ]
    ),
  ]);

  return h("div.filter-card", [
    h(Card, [h(FilterAccordian, { content: Buttons, text: "Embargo Status" })]),
  ]);
}
