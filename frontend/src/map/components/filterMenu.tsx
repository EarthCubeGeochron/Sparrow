import { useState } from "react";
import h from "@macrostrat/hyper";
import "../cluster.css";
import { AdminFilter } from "../../filter";
import { createParamsFromURL } from "../../admin/AdminPage";
import { Popover, Button, Tooltip } from "@blueprintjs/core";

export function FilterMenu({ hide = true, on_map, changeParams }) {
  const possibleFilters = ["public", "geometry", "date_range"]; //needs to work with "doi_like"

  const initialState = createParamsFromURL(possibleFilters);

  const [params, setParams] = useState(initialState);

  const createParams = (params) => {
    for (let [key, value] of Object.entries(params)) {
      if (value == null) {
        delete params[key];
      }
    }
    setParams(params);
    changeParams(params);
  };

  const dropDown = () => {
    return h(
      Popover,
      {
        content: h(AdminFilter, {
          possibleFilters,
          createParams,
          initParams: params || {},
          dropdown: true,
        }),
        minimal: true,
        position: "bottom",
      },
      [
        h(Tooltip, { content: "Choose Multiple Filters" }, [
          h(Button, { icon: "filter", minimal: true }),
        ]),
      ]
    );
  };

  return h(dropDown);
}
