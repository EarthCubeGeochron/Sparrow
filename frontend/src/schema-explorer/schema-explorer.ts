import React, { useState, useEffect, useContext } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Button, Collapse, Tab, Tabs, TextArea } from "@blueprintjs/core";
import { SchemaExplorerContext } from "./context";
import { capitalize, MinimalNavbar } from "~/components";
import { Link } from "react-router-dom";
import { SchemaTree } from "./schema-tree";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

function SchemaModelButtons() {
  const { state, runAction } = useContext(SchemaExplorerContext);
  let path = "/admin/schema-explorer/";

  return h("div.button-container", [
    state.modelsToShow.map((key, i) => {
      return h("div.model-button", { key: i }, [
        h(Link, { to: path + key, style: { textDecoration: "none" } }, [
          h(
            Button,
            {
              intent: state.model == key ? "primary" : "none",
              key: i
            },
            [key]
          )
        ])
      ]);
    })
  ]);
}

function SchemaNavBar() {
  const { state } = useContext(SchemaExplorerContext);
  const [open, setOpen] = useState(state.model == null);

  return h(MinimalNavbar, { className: "schema-nav" }, [
    h("div.button-nav-bar", [
      h(Link, { to: "/admin/schema-explorer" }, [h("h2", "Schema Explorer")])
    ]),
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

function SchemaExplorer({ model }) {
  const { state, runAction } = useContext(SchemaExplorerContext);
  console.log(state, model);
  useEffect(() => {
    if (state.possibleModels) {
      runAction({ type: "switch-model", payload: { model } });
    }
  }, [state.possibleModels, model]);

  return h("div", [h(SchemaNavBar), h.if(state.model != null)(SchemaTree)]);
}

export { SchemaExplorer };
