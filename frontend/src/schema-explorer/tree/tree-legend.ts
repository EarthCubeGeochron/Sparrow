import { hyperStyled } from "@macrostrat/hyper";
import { Divider } from "@blueprintjs/core";
import React, { useContext, useEffect, useState } from "react";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

function TreeLegend() {
  return h("div", [
    h("h3", "Help"),
    h(Divider),
    h("div.legend-field", [
      h("div.required", "field*"),
      h("div.legend", ": required field to import model")
    ]),
    h("div.legend-field", [
      h("b.type-schema", "SchemaName[]"),
      h(
        "div.legend",
        ": field represents a nested schema, [] at end signifies the field accepts a list of data schemas."
      )
    ]),
    h("div.legend-field", [
      h("b", "type_of"),
      h(
        "div.legend",
        ": this field represents a hierarchical relationship, i.e this model is a subset of this other."
      )
    ])
  ]);
}

export { TreeLegend };
