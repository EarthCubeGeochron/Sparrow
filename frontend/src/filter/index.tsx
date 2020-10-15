import { Button, Tooltip, Card, Popover, Icon } from "@blueprintjs/core";
import {
  AgeSlideSelect,
  DatePicker,
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

  const filterCard = () => {
    return h(Card, [
      h(AgeSlideSelect),
      h(DatePicker),
      h(GeologicFormationSelector),
      h.if(!on_map)(MapSelector),
    ]);
  };

  return h("div", [
    h(
      Popover,
      {
        content: h(filterCard),
        minimal: true,
        position: "bottom",
      },
      [
        h(Tooltip, { content: "Choose Multiple Filters" }, [
          h(Button, { onClick: toggleOpen, minimal: true }, [
            h(Icon, { icon: "filter" }),
          ]),
        ]),
      ]
    ),
  ]);
}

export { SampleFilter };
