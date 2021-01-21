import React, { useState } from "react";
import { Switch, Checkbox } from "@blueprintjs/core";
import h from "@macrostrat/hyper";

/**
 *
 * @param props function to update state of parent component, build get request params
 *
 * function to change
 */
export function EmabrgoSwitch(props) {
  const { updateEmbargoFilter } = props;
  const [checked, setChecked] = useState(false);
  const [checkbox, setCheckBox] = useState(false);

  const handleChange = () => {
    setChecked(!checked);
    updateEmbargoFilter("public", checked);
  };

  const handleCheckBox = () => {
    setCheckBox(!checkbox);
    if (!checkbox) {
      // the defualt switch is true, public only
      updateEmbargoFilter("public", true);
    } else {
      // if it's unclicked need to clear params
      updateEmbargoFilter("public", null);
    }
  };

  const Switcher = !checkbox
    ? null
    : h(Switch, {
        checked,
        innerLabel: "Public Only",
        innerLabelChecked: "Private Only",
        onChange: handleChange,
      });

  return h("div", [
    h(Checkbox, {
      checked: checkbox,
      onChange: handleCheckBox,
      labelElement: "Filter by Embargo Status",
    }),
    Switcher,
  ]);
}
