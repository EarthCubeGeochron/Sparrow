import { hyperStyled } from "@macrostrat/hyper";
import React, { useContext } from "react";
import { Divider } from "@blueprintjs/core";
import { SchemaExplorerContext } from "./context";
import { JsonTree, Tree, TreeLegend } from "./tree";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

const defaultSchema = {
  description: null,
  nullable: false,
  required: true,
  read_only: false,
  type: null
};
function SchemaTree() {
  const { state } = useContext(SchemaExplorerContext);

  return h("div.schema-tree", [
    h(Tree, { fieldName: state.model, link: state.route, ...defaultSchema }),
    h(Divider),
    h("div.json-tree-container", [
      h(JsonTree, {
        fieldName: state.model,
        link: state.route,
        ...defaultSchema
      }),
      h(TreeLegend)
    ])
  ]);
}

export { SchemaTree };
