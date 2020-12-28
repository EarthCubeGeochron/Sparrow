import React from "react";
import h from "@macrostrat/hyper";
import { InputGroup } from "@blueprintjs/core";

export function DoiFilter(props) {
  const { updateDoi } = props;

  const handleChange = (e) => {
    updateDoi("doi_like", e.target.value);
  };

  return h("div", [
    "Search for DOI",
    h(InputGroup, { onChange: handleChange }),
  ]);
}
