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

const buttonHierarchy = {
  primary: ["project", "sample", "session", "analysis", "datum", "data_file"],
  secondary: [
    "sample_geo_entity",
    "geo_entity",
    "material",
    "instrument",
    "method",
    "researcher",
    "publication",
    "tag"
  ],
  tertiary: ["attribute", "authority", "datum_type", "unit", "error_metric"]
};

function SchemaModelButtons() {
  const { state, runAction } = useContext(SchemaExplorerContext);
  let path = "/admin/schema-explorer/";

  return h("div", [
    Object.entries(buttonHierarchy).map(([hierarchy, buttons], i) => {
      return h("div.button-container", { key: i }, [
        buttons.map((key, i) => {
          return h("div.model-button", { key: i }, [
            h(Link, { to: path + key, style: { textDecoration: "none" } }, [
              h(
                Button,
                {
                  style: hierarchy == "primary" ? { fontWeight: "bold" } : {},
                  intent: state.model == key ? "primary" : "none",
                  key: i
                },
                [capitalize(key)]
              )
            ])
          ]);
        })
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

function SchemaExplorer({ model }) {
  const { state, runAction } = useContext(SchemaExplorerContext);

  console.log(state);

  useEffect(() => {
    if (state.possibleModels) {
      runAction({ type: "switch-model", payload: { model } });
    }
  }, [state.possibleModels, model]);

  return h("div", [h(SchemaNavBar), h.if(state.model != null)(SchemaTree)]);
}

export { SchemaExplorer };
