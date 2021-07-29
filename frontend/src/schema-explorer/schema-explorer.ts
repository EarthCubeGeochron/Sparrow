import React, { useState, useEffect, useContext } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import ReactJson from "react-json-view";
import { Button } from "@blueprintjs/core";
import { SchemaExplorerContext } from "./context";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

function SchemaModelButtons() {
  const { state, runAction } = useContext(SchemaExplorerContext);

  const onModelButtonClick = model => {
    runAction({
      type: "switch-model",
      payload: { model }
    });
  };

  return h("div.button-container", [
    Object.keys(state.possibleModels).map((key, i) => {
      return h("div.model-button", { key: i }, [
        h(
          Button,
          {
            key: i,
            onClick: () => onModelButtonClick(key)
          },
          [key]
        )
      ]);
    })
  ]);
}

function SchemaExplorer() {
  const { state, runAction } = useContext(SchemaExplorerContext);
  console.log(state);

  const onSelect = select => {
    console.log(select);
    let namespace = select.namespace[0];
    if (state.possibleModels[namespace]) {
      runAction({ type: "switch-model", payload: { model: namespace } });
    }
  };

  return h("div", [
    "SCHEMA EXPLORER!!!",
    h(SchemaModelButtons),
    h(ReactJson, {
      src: state.fields,
      name: state.model,
      onSelect,
      collapsed: 1,
      displayDataTypes: false
    })
  ]);
}

export { SchemaExplorer };
