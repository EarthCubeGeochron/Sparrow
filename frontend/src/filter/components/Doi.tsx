import React from "react";
import { InputGroup, Card } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function DoiFilter(props) {
  const { updateDoi } = props;

  const handleChange = (e) => {
    updateDoi("doi_like", e.target.value);
  };

  return h("div.filter-card", [
    h(Card, [
      h("div", ["Search for DOI:", h(InputGroup, { onChange: handleChange })]),
    ]),
  ]);
}
