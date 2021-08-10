import React, { useState, useEffect, useContext } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Button, Collapse, Tab, Tabs, TextArea } from "@blueprintjs/core";
import { SchemaExplorerContext } from "./context";
import ReactJson from "react-json-view";
import { MinimalNavbar } from "~/components";
import { SchemaTree } from "./schema-tree";
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

function SchemaNavBar() {
  const { state } = useContext(SchemaExplorerContext);
  const [open, setOpen] = useState(false);
  return h("div", [
    h(MinimalNavbar, [
      h("h2", "Schema Explorer"),
      h("h4", `Current Model: ${state.model}`)
    ]),
    h(MinimalNavbar, [
      h("div", [
        h("div.button-nav-bar", [
          h("h4", "Choose a data model to view the schema"),
          h(Button, {
            minimal: true,
            icon: "menu",
            onClick: () => setOpen(!open)
          })
        ]),
        h(Collapse, { isOpen: open }, [h(SchemaModelButtons)])
      ])
    ])
  ]);
}

function SchemaExample() {
  const { state } = useContext(SchemaExplorerContext);

  return h("div", [h("h3", `Example JSON for ${state.model}`)]);
}

function SchemaTest() {
  const { state } = useContext(SchemaExplorerContext);
  const initText: string = `Paste your JSON object for ${state.model}`;
  const [text, setText] = useState<string>(initText);

  const onChange = e => {
    setText(e.target.value);
  };
  return h("div", [
    h("h3", "Test Your JSON"),
    h("div.text-box", [
      h(TextArea, {
        onChange,
        value: text,
        fill: true,
        style: { height: "250px", width: "250px" }
      })
    ]),
    h(Button, { intent: "primary" }, ["Submit"])
  ]);
}

function SchemaTabs() {
  return h(Tabs, { id: "schema-tabs" }, [
    h(Tab, { id: "example", panel: h(SchemaExample), title: "Example JSON" }),
    h(Tab, { id: "test", panel: h(SchemaTest), title: "Test JSON Validatity" })
  ]);
}

function SchemaExplorer() {
  const { state, runAction } = useContext(SchemaExplorerContext);

  return h("div", [
    h(SchemaNavBar),
    h("div.body", [h(SchemaTree), h(SchemaTabs)])
  ]);
}

export { SchemaExplorer };
