import { useState, useReducer } from "react";
import { reducer } from "./reducers-filters";
import { Button, Tooltip, Card, Popover, Icon } from "@blueprintjs/core";
import {
  AgeSlideSelect,
  DatePicker,
  GeologicFormationSelector,
  //MapSelector,
} from "./components";
import { useToggle, useAPIResult } from "../map/components/APIResult";
import h from "@macrostrat/hyper";
import { EmabrgoSwitch } from "./components/Embargo";

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
      h(DatePicker, { updateDateRange: () => {} }),
      h(GeologicFormationSelector),
      //h.if(!on_map)(MapSelector),
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

/**
 *
 * Component that will sit at the top of every admin page infinite scroll.
 *
 * It will have a set of filters to choose from and an Apply button
 *
 * Once Apply button is clicked, a params object will created from the values selected
 * and a new get request will be issues. At least thats the idea
 */
function AdminFilter(props) {
  // need a prop that grabs set to create params
  const { createParams } = props;

  const [params, dispatch] = useReducer(reducer, {});

  const updateParams = (field, data) => {
    if (field == "date_range") {
      dispatch({ type: "date_range", payload: { dates: data } });
    }
    if (field == "public") {
      dispatch({ type: "public", payload: { embargoed: data } });
    }
  };

  const SumbitFilterButton = () => {
    const onSubmit = () => {
      createParams(params);
    };

    return h(
      Button,
      {
        intent: "primary",
        onClick: onSubmit,
      },
      ["Apply Filters"]
    );
  };

  return h("div", [
    h(EmabrgoSwitch, { updateEmbargoFilter: updateParams }),
    h(DatePicker, { updateDateRange: updateParams }),
    h(SumbitFilterButton),
  ]);
}

export { SampleFilter, AdminFilter };
