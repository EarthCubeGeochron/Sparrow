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
interface Filter {
  on_map?: boolean;
}

function SampleFilter({ on_map = false }: Filter) {
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
}

export { SampleFilter };
