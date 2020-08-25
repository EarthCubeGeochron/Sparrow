import * as React from "react";
import { Button, Tooltip, Collapse, Card, MenuItem } from "@blueprintjs/core";
import {
  AgeSlideSelect,
  DatePicker,
  MultipleSelectFilter,
  GeologicFormationSelector,
  MapSelector,
} from "./components";
import { useToggle, useAPIResult } from "../map/components/APIResult";
import h from "@macrostrat/hyper";

/**
 * This Functional Component is a filter template to be used on different
 * pages. Some of the filters may be hidden depending on what page the user
 * is on, (i.e. a location selector wouldn't be rendered on the MapPanel
 */
interface filter {
  on_map?: boolean;
}

const SampleFilter = ({ on_map = false }) => {
  const [open, toggleOpen] = useToggle(false);

  return h("div", [
    h(Tooltip, { content: "Choose Multiple Filters" }, [
      h(Button, { onClick: toggleOpen, icon: "filter" }),
    ]),
    h(Collapse, { isOpen: open }, [
      h(Card, [
        h(AgeSlideSelect),
        h(DatePicker),
        h(GeologicFormationSelector),
        h.if(!on_map)(MapSelector),
      ]),
    ]),
  ]);
};

export { SampleFilter };
