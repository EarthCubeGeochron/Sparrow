import { useState } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import React, { useContext } from "react";
import { Divider } from "@blueprintjs/core";
import { SchemaExplorerContext } from "./context";
import { JsonTree, Tree, TreeLegend } from "./tree";
import { CollapsePanel } from "@macrostrat/ui-components";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

const defaultSchema = {
  description: null,
  nullable: false,
  required: true,
  read_only: false,
  type: null,
};
function SchemaTree() {
  const { state } = useContext(SchemaExplorerContext);

  const [json, setJSON] = useState({});

  const onChange = (j, p) => {
    setJSON(j);
  };

  return h("div", [
    h("div.schema-tree", [
      h(Tree, {
        fieldName: state.model,
        link: state.route,
        onChange,
        ...defaultSchema,
      }),
      h(Divider),
      h("div.right-panel", [
        h(TreeLegend),
        h(
          CollapsePanel,
          {
            title: `Example JSON for ${state.model}`,
            storageID: "json-example",
          },
          h("div.json-tree-container", [
            h(JsonTree, {
              fieldName: state.model,
              json,
              link: state.route,
              ...defaultSchema,
            }),
          ])
        ),
      ]),
    ]),
  ]);
}

export { SchemaTree };
