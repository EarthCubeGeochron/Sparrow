import { hyperStyled } from "@macrostrat/hyper";
import { Card } from "@blueprintjs/core";
import { SchemaExplorerContext } from "../context";
import React, { useContext, useEffect, useState } from "react";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

function TreeLegend() {
  return h(Card, { className: "legend-card" }, [
    h("h3", "Legend"),
    h("div.legend-field", [
      h("div.read-only", "Read-Only"),
      h("div.legend", ": handled automatically on import")
    ]),
    h("div.legend-field", [
      h("div.required", "*"),
      h("div.legend", ": required field to import model")
    ]),
    h("div.legend-field", [
      h("div.type-schema", "SchemaName[]"),
      h(
        "div.legend",
        ": field represents a nested schema, [] at end signifies the field accepts a list of data schemas."
      )
    ])
  ]);
}

export { TreeLegend };
